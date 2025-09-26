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

        try:
            response = ragChain.get_answer(prompt_validated)
            response_data = {
                "response": f"{response}"
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception:
            return Response({"error": "error server"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

