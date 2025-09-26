from rest_framework.views import APIView
from .serializer import generateResponseSerializer
from rest_framework.response import Response
from rest_framework import status
from . import ragChain

class generateResponseView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = generateResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        prompt_validated = serializer.validated_data['prompt']
        print("validou o prompt pelo serializer:", prompt_validated)
        try:
            response = ragChain.get_answer(prompt_validated)
            response_data = {
                "response_text": response.content,
                "metadata": {
                    "model": response.response_metadata.get('model_name', 'N/A'),
                    "total_tokens": response.usage_metadata.get('total_tokens', 0)
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception:
            return Response({"error": "error server"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

