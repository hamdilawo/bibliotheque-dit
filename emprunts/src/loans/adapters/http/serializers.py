
from rest_framework import serializers


class BorrowABookResponseSerializer(serializers.Serializer):
    loan_id = serializers.UUIDField(source="id")
    borrower_id = serializers.CharField()
    borrower_name = serializers.CharField(source="reader.name")
    borrower_email = serializers.CharField(source="reader.email")
    borrowed_book = serializers.CharField(source="book.title")
    borrowed_book_id = serializers.CharField(source="book.id")


class CreerEmpruntSerializer(serializers.Serializer):
    """Serializer pour créer un emprunt."""
    book_id = serializers.CharField()
    term = serializers.DateField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class RetourEmpruntSerializer(serializers.Serializer):
    """Serializer pour enregistrer un retour."""
    loan_id = serializers.UUIDField()


class ReturnLoanResponseSerializer(serializers.Serializer):
    loan_id = serializers.UUIDField(source="id")
    borrower_id = serializers.CharField()
    borrower_name = serializers.CharField(source="reader.name")
    borrower_email = serializers.CharField(source="reader.email")
    borrowed_book = serializers.CharField(source="book.title")
    borrowed_book_id = serializers.CharField(source="book.id")
