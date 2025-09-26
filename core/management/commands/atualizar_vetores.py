from django.core.management.base import BaseCommand, CommandError

try:
    from ... import dataBaseVector
except ImportError:
    raise ImportError(
        "Não foi possível importar o módulo 'dataBaseVector' de 'core'. "
        "Verifique se o arquivo 'core/dataBaseVector.py' existe."
    )

class Command(BaseCommand):
    help = 'Executa o pipeline completo de carregamento e vetorização de documentos.'

    def handle(self, *args, **kwargs):
        try:
            documents = dataBaseVector.load_all_documents()

            if not documents:
                return

            chunks = dataBaseVector.divide_documents_in_chunks(documents)
            dataBaseVector.add_to_chroma(chunks)

        except Exception as e:
            raise CommandError(f"Erro durante a execução do pipeline: {e}")