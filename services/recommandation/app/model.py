"""Hybrid recommender model based on CF (SVD) and content (TF-IDF)."""
import ast
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class RecommendationModel:
    def __init__(self):
        self.artifacts: Dict[str, object] = {}
        self.ratings: Optional[pd.DataFrame] = None
        self.metrics: Dict[str, object] = {}
        self.is_trained = False

    @staticmethod
    def normalize_isbn(value) -> str:
        if pd.isna(value):
            return ""
        s = str(value).strip()
        return "".join([c for c in s if c.isdigit() or c in ("X", "x")]).upper()

    @staticmethod
    def parse_categories(value) -> List[str]:
        if pd.isna(value):
            return []
        if isinstance(value, list):
            return [str(v) for v in value]
        s = str(value).strip()
        try:
            if s.startswith("["):
                parsed = ast.literal_eval(s)
                if isinstance(parsed, list):
                    return [str(v) for v in parsed]
        except Exception:
            pass
        return [s] if s else []

    @classmethod
    def preparer_livres(cls, books_df: pd.DataFrame) -> pd.DataFrame:
        df = books_df.copy()

        rename_map = {
            "titre": "title",
            "auteur": "author",
            "isbn": "ISBN_13",
            "categorie_nom": "categorie",
            "editeur": "publishers",
        }
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

        if "ISBN_13" not in df.columns and "book_isbn" in df.columns:
            df = df.rename(columns={"book_isbn": "ISBN_13"})

        for col in ["title", "author", "categorie", "publishers", "ISBN_13"]:
            if col not in df.columns:
                df[col] = ""

        if "livre_id" not in df.columns:
            if "id" in df.columns:
                df["livre_id"] = pd.to_numeric(df["id"], errors="coerce")
            else:
                df["livre_id"] = np.nan

        df["isbn_norm"] = df["ISBN_13"].apply(cls.normalize_isbn)
        df = df[df["isbn_norm"] != ""].drop_duplicates(subset=["isbn_norm"])
        return df[["livre_id", "isbn_norm", "title", "author", "categorie", "publishers", "ISBN_13"]]

    @classmethod
    def preparer_emprunts(
        cls,
        emprunts_df: pd.DataFrame,
        livre_id_to_isbn: Optional[Dict[int, str]] = None,
    ) -> pd.DataFrame:
        df = emprunts_df.copy()
        if "utilisateur_id" in df.columns:
            df = df.rename(columns={"utilisateur_id": "user_id"})

        isbn_col = None
        for candidate in ["ISBN_13", "book_isbn", "isbn", "isbn_13", "livre_isbn"]:
            if candidate in df.columns:
                isbn_col = candidate
                break

        if isbn_col is None and "livre_id" in df.columns and livre_id_to_isbn:
            df["isbn_norm"] = df["livre_id"].map(livre_id_to_isbn).apply(cls.normalize_isbn)
        elif isbn_col is not None:
            df["isbn_norm"] = df[isbn_col].apply(cls.normalize_isbn)
        else:
            df["isbn_norm"] = ""

        if "note" not in df.columns:
            if "rating" in df.columns:
                df["note"] = df["rating"]
            elif "score" in df.columns:
                df["note"] = df["score"]
            elif "jours_retard" in df.columns:
                retard = pd.to_numeric(df["jours_retard"], errors="coerce").fillna(0)
                df["note"] = np.where(retard <= 0, 1.5, np.where(retard <= 7, 1.0, 0.8))
            else:
                df["note"] = 1.0

        df["note"] = pd.to_numeric(df["note"], errors="coerce")
        df = df.dropna(subset=["user_id", "note"])
        df = df[df["isbn_norm"] != ""]

        ratings = df.groupby(["user_id", "isbn_norm"], as_index=False)["note"].mean()
        return ratings

    @classmethod
    def _normalize_ratings_schema(cls, ratings: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
        if ratings is None or not isinstance(ratings, pd.DataFrame):
            return None

        df = ratings.copy()
        if "user_id" not in df.columns and "utilisateur_id" in df.columns:
            df = df.rename(columns={"utilisateur_id": "user_id"})
        if "user_id" not in df.columns:
            return None

        if "isbn_norm" not in df.columns:
            source = None
            for candidate in ["ISBN_13", "book_isbn", "isbn", "isbn_13", "livre_isbn"]:
                if candidate in df.columns:
                    source = candidate
                    break
            if source is not None:
                df["isbn_norm"] = df[source].apply(cls.normalize_isbn)
        else:
            df["isbn_norm"] = df["isbn_norm"].apply(cls.normalize_isbn)

        if "isbn_norm" not in df.columns:
            return None

        if "note" not in df.columns:
            if "rating" in df.columns:
                df["note"] = df["rating"]
            elif "score" in df.columns:
                df["note"] = df["score"]
            else:
                df["note"] = 1.0

        df["note"] = pd.to_numeric(df["note"], errors="coerce")
        df = df.dropna(subset=["user_id", "note"])
        df = df[df["isbn_norm"] != ""]
        if df.empty:
            return None
        return df

    @classmethod
    def _normalize_books_meta_schema(
        cls,
        books_meta: Optional[pd.DataFrame],
        fallback_isbns: Optional[List[str]] = None,
    ) -> Optional[pd.DataFrame]:
        if books_meta is None or not isinstance(books_meta, pd.DataFrame):
            if fallback_isbns is None:
                return None
            return pd.DataFrame({
                "livre_id": np.nan,
                "isbn_norm": list(fallback_isbns),
                "title": "",
                "author": "",
                "categorie": "",
                "publishers": "",
            })

        df = books_meta.copy()
        if "isbn_norm" not in df.columns:
            source = None
            for candidate in ["ISBN_13", "book_isbn", "isbn", "isbn_13", "livre_isbn"]:
                if candidate in df.columns:
                    source = candidate
                    break
            if source is not None:
                df["isbn_norm"] = df[source].apply(cls.normalize_isbn)
            elif df.index.name == "isbn_norm":
                df = df.reset_index()

        if "isbn_norm" not in df.columns:
            if fallback_isbns is None:
                return None
            return pd.DataFrame({
                "livre_id": np.nan,
                "isbn_norm": list(fallback_isbns),
                "title": "",
                "author": "",
                "categorie": "",
                "publishers": "",
            })

        df["isbn_norm"] = df["isbn_norm"].apply(cls.normalize_isbn)
        df = df[df["isbn_norm"] != ""].drop_duplicates(subset=["isbn_norm"])

        if "livre_id" not in df.columns:
            if "id" in df.columns:
                df["livre_id"] = pd.to_numeric(df["id"], errors="coerce")
            else:
                df["livre_id"] = np.nan

        for col in ["title", "author", "categorie", "publishers"]:
            if col not in df.columns:
                df[col] = ""
        return df

    def entrainer(
        self,
        emprunts_df: pd.DataFrame,
        books_df: pd.DataFrame,
        livre_id_to_isbn: Optional[Dict[int, str]] = None,
        alpha: float = 0.6,
        min_user_ratings: int = 3,
        random_state: int = 42,
    ) -> dict:
        books_meta = self.preparer_livres(books_df)
        ratings = self.preparer_emprunts(emprunts_df, livre_id_to_isbn=livre_id_to_isbn)

        if ratings.empty:
            raise ValueError("No ratings available to train the model.")

        ratings_enriched = ratings.merge(
            books_meta[["livre_id", "isbn_norm", "title", "author", "categorie", "publishers"]],
            on="isbn_norm",
            how="inner",
        )

        if ratings_enriched.empty:
            logger.warning("No overlap between ratings and books metadata; disabling content features.")
            books_meta = pd.DataFrame({
                "livre_id": np.nan,
                "isbn_norm": ratings["isbn_norm"].unique(),
                "title": "",
                "author": "",
                "categorie": "",
                "publishers": "",
                "ISBN_13": "",
            })
            ratings_enriched = ratings.copy()

        user_ids = ratings_enriched["user_id"].unique()
        item_ids = ratings_enriched["isbn_norm"].unique()

        user_index = {u: i for i, u in enumerate(user_ids)}
        item_index = {b: i for i, b in enumerate(item_ids)}

        rows = ratings_enriched["user_id"].map(user_index).astype(int)
        cols = ratings_enriched["isbn_norm"].map(item_index).astype(int)
        data = ratings_enriched["note"].astype(float)
        rating_matrix = csr_matrix((data, (rows, cols)), shape=(len(user_ids), len(item_ids)))

        svd = None
        user_factors = None
        item_factors = None
        variance_expliquee = 0.0
        if min(rating_matrix.shape) > 1:
            n_components = min(50, min(rating_matrix.shape) - 1)
            svd = TruncatedSVD(n_components=n_components, random_state=random_state)
            user_factors = svd.fit_transform(rating_matrix)
            item_factors = svd.components_.T
            variance_expliquee = float(svd.explained_variance_ratio_.sum())

        popularity = ratings_enriched.groupby("isbn_norm")["note"].agg(["mean", "count"])
        popularity["score"] = popularity["mean"] * np.log1p(popularity["count"])
        error_metrics = self._compute_error_metrics(
            ratings_enriched=ratings_enriched,
            user_index=user_index,
            item_index=item_index,
            user_factors=user_factors,
            item_factors=item_factors,
            popularity=popularity,
        )

        books_meta = books_meta.copy()
        books_meta["categorie_list"] = books_meta["categorie"].apply(self.parse_categories)
        books_meta["content_text"] = (
            books_meta["title"].fillna("").astype(str)
            + " "
            + books_meta["author"].fillna("").astype(str)
            + " "
            + books_meta["publishers"].fillna("").astype(str)
            + " "
            + books_meta["categorie_list"].apply(lambda lst: " ".join(lst))
        ).str.lower()

        vectorizer = None
        tfidf = None
        if not books_meta["content_text"].str.strip().eq("").all():
            try:
                vectorizer = TfidfVectorizer(min_df=2, max_features=50000)
                tfidf = vectorizer.fit_transform(books_meta["content_text"])
            except ValueError:
                vectorizer = TfidfVectorizer(min_df=1, max_features=50000)
                tfidf = vectorizer.fit_transform(books_meta["content_text"])

        book_index = {isbn: i for i, isbn in enumerate(books_meta["isbn_norm"].values)}

        self.artifacts = {
            "svd": svd,
            "user_factors": user_factors,
            "item_factors": item_factors,
            "user_ids": user_ids,
            "item_ids": item_ids,
            "user_index": user_index,
            "item_index": item_index,
            "vectorizer": vectorizer,
            "tfidf": tfidf,
            "books_meta": books_meta,
            "book_index": book_index,
            "popularity": popularity,
            "alpha": alpha,
            "min_user_ratings": min_user_ratings,
        }

        self.ratings = ratings_enriched[["user_id", "isbn_norm", "note"]]
        sparsity = 1.0 - (len(self.ratings) / (len(user_ids) * len(item_ids))) if len(user_ids) and len(item_ids) else 1.0
        self.metrics = {
            "n_utilisateurs": len(user_ids),
            "n_livres": len(item_ids),
            "n_emprunts": len(self.ratings),
            "variance_expliquee": round(variance_expliquee, 4),
            "sparsity": round(float(sparsity), 4),
            "rmse": error_metrics["rmse"],
            "mae": error_metrics["mae"],
        }
        self.is_trained = True
        return self.metrics

    def _compute_error_metrics(
        self,
        ratings_enriched: pd.DataFrame,
        user_index: Dict[object, int],
        item_index: Dict[str, int],
        user_factors,
        item_factors,
        popularity: pd.DataFrame,
    ) -> Dict[str, Optional[float]]:
        if ratings_enriched is None or ratings_enriched.empty:
            return {"rmse": None, "mae": None}

        y_true = ratings_enriched["note"].astype(float).to_numpy()
        preds = np.full(len(ratings_enriched), np.nan, dtype=float)

        if user_factors is not None and item_factors is not None:
            row_ids = ratings_enriched["user_id"].map(user_index)
            col_ids = ratings_enriched["isbn_norm"].map(item_index)
            valid = row_ids.notna() & col_ids.notna()
            if valid.any():
                r_idx = row_ids[valid].astype(int).to_numpy()
                c_idx = col_ids[valid].astype(int).to_numpy()
                preds[valid.to_numpy()] = np.sum(user_factors[r_idx] * item_factors[c_idx], axis=1)

        fallback = ratings_enriched["isbn_norm"].map(popularity["mean"]).astype(float).to_numpy()
        global_mean = float(np.nanmean(y_true)) if len(y_true) else 0.0
        fallback = np.where(np.isnan(fallback), global_mean, fallback)
        preds = np.where(np.isnan(preds), fallback, preds)

        errors = preds - y_true
        rmse = float(np.sqrt(np.mean(errors ** 2)))
        mae = float(np.mean(np.abs(errors)))
        return {"rmse": round(rmse, 4), "mae": round(mae, 4)}

    def _minmax(self, series: pd.Series) -> pd.Series:
        s = series.astype(float)
        if s.empty:
            return s
        min_val = s.min()
        max_val = s.max()
        if max_val == min_val:
            return pd.Series(0.0, index=s.index)
        return (s - min_val) / (max_val - min_val)

    def _cf_scores_for_user(self, user_id, artifacts: dict) -> Optional[pd.Series]:
        user_index = artifacts.get("user_index", {})
        user_factors = artifacts.get("user_factors")
        item_factors = artifacts.get("item_factors")
        item_ids = artifacts.get("item_ids", [])

        if user_factors is None or item_factors is None:
            return None
        idx = user_index.get(user_id)
        if idx is None:
            return None
        scores = user_factors[idx].dot(item_factors.T)
        return pd.Series(scores, index=item_ids)

    def _content_scores_for_user(
        self,
        user_id,
        ratings: pd.DataFrame,
        artifacts: dict,
    ) -> Optional[pd.Series]:
        ratings = self._normalize_ratings_schema(ratings)
        tfidf = artifacts.get("tfidf")
        book_index = artifacts.get("book_index", {})
        books_meta = self._normalize_books_meta_schema(artifacts.get("books_meta"))

        if tfidf is None or books_meta is None or ratings is None:
            return None
        if "isbn_norm" not in ratings.columns:
            return None

        user_ratings = ratings[ratings["user_id"] == user_id]
        if user_ratings.empty:
            return None
        if "isbn_norm" not in user_ratings.columns:
            return None

        idx = user_ratings["isbn_norm"].map(book_index).dropna().astype(int)
        if idx.empty:
            return None

        weights = user_ratings.loc[idx.index, "note"].astype(float).values
        profile = tfidf[idx].T.dot(weights)
        if hasattr(profile, "toarray"):
            profile = profile.toarray()
        profile = np.asarray(profile).reshape(1, -1)
        scores = cosine_similarity(profile, tfidf).ravel()
        return pd.Series(scores, index=books_meta["isbn_norm"].values)

    def recommander(
        self,
        utilisateur_id,
        n: int = 5,
        ratings: Optional[pd.DataFrame] = None,
        ref_isbn: Optional[str] = None,
        ref_weight: float = 0.3,
    ) -> List[dict]:
        if not self.is_trained:
            raise RuntimeError("Model is not trained yet.")

        artifacts = self.artifacts
        ratings_df = self._normalize_ratings_schema(ratings if ratings is not None else self.ratings)

        utilisateur_id = self._resolve_user_id(utilisateur_id, artifacts)

        popularity = artifacts.get("popularity")
        if popularity is None or "score" not in popularity:
            raise RuntimeError("Popularity data is missing from artifacts.")

        min_user_ratings = artifacts.get("min_user_ratings", 3)
        alpha = artifacts.get("alpha", 0.6)

        user_hist = ratings_df[ratings_df["user_id"] == utilisateur_id] if ratings_df is not None else pd.DataFrame()
        seen = set(user_hist["isbn_norm"]) if (not user_hist.empty and "isbn_norm" in user_hist.columns) else set()

        if len(user_hist) < min_user_ratings:
            content = self._content_scores_for_user(utilisateur_id, ratings_df, artifacts)
            scores = content if content is not None else popularity["score"]
        else:
            cf = self._cf_scores_for_user(utilisateur_id, artifacts)
            content = self._content_scores_for_user(utilisateur_id, ratings_df, artifacts)
            if cf is None and content is None:
                scores = popularity["score"]
            elif cf is None:
                scores = content
            elif content is None:
                scores = cf
            else:
                cf_n = self._minmax(cf)
                content_n = self._minmax(content.reindex(cf_n.index).fillna(0.0))
                scores = alpha * cf_n + (1.0 - alpha) * content_n

        scores = scores.drop(labels=seen, errors="ignore")
        top = scores.sort_values(ascending=False).head(n)

        books_meta = self._normalize_books_meta_schema(artifacts.get("books_meta"), fallback_isbns=top.index)
        if books_meta is None:
            recs = pd.DataFrame({"isbn_norm": top.index, "score": top.values})
        else:
            recs = books_meta.set_index("isbn_norm").reindex(top.index).copy()
            recs.index.name = "isbn_norm"
            recs["score"] = top.values
            recs = recs.reset_index()

        if ref_isbn:
            recs = self._blend_with_reference(recs, ref_isbn, artifacts, weight=ref_weight)
            recs = recs.sort_values("final_score", ascending=False).head(n)
            recs["score"] = recs["final_score"]

        for col in ["isbn_norm", "title", "author", "categorie", "publishers"]:
            if col not in recs.columns:
                recs[col] = ""
        if "livre_id" not in recs.columns:
            recs["livre_id"] = np.nan
        return recs[["livre_id", "isbn_norm", "title", "author", "categorie", "publishers", "score"]].to_dict("records")

    def recommander_depuis_historique(
        self,
        utilisateur_id,
        n: int = 5,
        ratings: Optional[pd.DataFrame] = None,
    ) -> List[dict]:
        if not self.is_trained:
            raise RuntimeError("Model is not trained yet.")

        artifacts = self.artifacts
        ratings_df = self._normalize_ratings_schema(ratings if ratings is not None else self.ratings)
        if ratings_df is None:
            return []

        utilisateur_id = self._resolve_user_id(utilisateur_id, artifacts)
        user_hist = ratings_df[ratings_df["user_id"] == utilisateur_id]
        if user_hist.empty or "isbn_norm" not in user_hist.columns:
            return []

        seen = set(user_hist["isbn_norm"])
        scores = self._content_scores_for_user(utilisateur_id, ratings_df, artifacts)
        if scores is None:
            return []

        scores = scores.drop(labels=seen, errors="ignore")
        top = scores.sort_values(ascending=False).head(n)

        books_meta = self._normalize_books_meta_schema(artifacts.get("books_meta"), fallback_isbns=top.index)
        if books_meta is None:
            recs = pd.DataFrame({"isbn_norm": top.index, "score": top.values})
        else:
            recs = books_meta.set_index("isbn_norm").reindex(top.index).copy()
            recs.index.name = "isbn_norm"
            recs["score"] = top.values
            recs = recs.reset_index()

        for col in ["isbn_norm", "title", "author", "categorie", "publishers"]:
            if col not in recs.columns:
                recs[col] = ""
        if "livre_id" not in recs.columns:
            recs["livre_id"] = np.nan
        return recs[["livre_id", "isbn_norm", "title", "author", "categorie", "publishers", "score"]].to_dict("records")

    def _resolve_user_id(self, user_id, artifacts: dict):
        user_index = artifacts.get("user_index", {})
        if user_id in user_index:
            return user_id
        if isinstance(user_id, str):
            if user_id.isdigit():
                as_int = int(user_id)
                if as_int in user_index:
                    return as_int
        else:
            as_str = str(user_id)
            if as_str in user_index:
                return as_str
        return user_id

    def _blend_with_reference(self, recs: pd.DataFrame, ref_isbn: str, artifacts: dict, weight: float = 0.3) -> pd.DataFrame:
        recs = recs.copy()
        recs["final_score"] = recs["score"]

        book_index = artifacts.get("book_index", {})
        tfidf = artifacts.get("tfidf")
        if tfidf is None:
            return recs

        key = self.normalize_isbn(ref_isbn)
        ref_idx = book_index.get(key)
        if ref_idx is None:
            return recs

        candidate_isbns = recs["isbn_norm"].values
        candidate_idx = [book_index.get(isbn) for isbn in candidate_isbns]

        sims = np.zeros(len(candidate_isbns))
        valid = [i for i, idx in enumerate(candidate_idx) if idx is not None]
        if valid:
            idx_arr = [candidate_idx[i] for i in valid]
            ref_vec = tfidf[ref_idx]
            sims_valid = cosine_similarity(ref_vec, tfidf[idx_arr]).ravel()
            sims[valid] = sims_valid

        base_n = self._minmax(recs["score"]).values
        ref_n = self._minmax(pd.Series(sims, index=recs.index)).values
        recs["final_score"] = (1.0 - weight) * base_n + weight * ref_n
        return recs

    def sauvegarder(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        payload = dict(self.artifacts)
        payload["__meta__"] = {"metrics": self.metrics}
        if self.ratings is not None:
            payload["__ratings__"] = self.ratings
        with open(path, "wb") as f:
            pickle.dump(payload, f)
        logger.info(f"Artifacts saved: {path}")

    @classmethod
    def charger(cls, path: str) -> "RecommendationModel":
        if not Path(path).exists():
            raise FileNotFoundError(f"No artifacts found at: {path}")
        with open(path, "rb") as f:
            obj = pickle.load(f)

        if isinstance(obj, cls):
            return obj

        model = cls()
        if isinstance(obj, dict):
            model.artifacts = {k: v for k, v in obj.items() if not k.startswith("__")}
            meta = obj.get("__meta__", {})
            model.metrics = meta.get("metrics", {}) or model._metrics_from_artifacts()
            ratings = obj.get("__ratings__")
            if isinstance(ratings, pd.DataFrame):
                model.ratings = model._normalize_ratings_schema(ratings)
            books_meta = model.artifacts.get("books_meta")
            if isinstance(books_meta, pd.DataFrame):
                model.artifacts["books_meta"] = model._normalize_books_meta_schema(books_meta)
            model.is_trained = True
            return model

        raise ValueError("Unsupported artifacts format.")

    def _metrics_from_artifacts(self) -> Dict[str, object]:
        artifacts = self.artifacts
        user_ids = artifacts.get("user_ids", [])
        item_ids = artifacts.get("item_ids", [])
        svd = artifacts.get("svd")
        variance = 0.0
        if svd is not None and hasattr(svd, "explained_variance_ratio_"):
            variance = float(np.sum(svd.explained_variance_ratio_))
        popularity = artifacts.get("popularity")
        n_emprunts = 0
        if isinstance(popularity, pd.DataFrame) and "count" in popularity.columns:
            n_emprunts = int(popularity["count"].sum())
        return {
            "n_utilisateurs": len(user_ids),
            "n_livres": len(item_ids),
            "n_emprunts": n_emprunts,
            "variance_expliquee": round(variance, 4),
            "rmse": None,
            "mae": None,
        }
