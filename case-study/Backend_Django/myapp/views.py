from django.http import JsonResponse
from openai import OpenAI
from .rag_Jina.model import query_json
from rest_framework.decorators import api_view
import traceback

client = OpenAI(api_key="Your-Key", base_url="https://api.deepseek.com")

@api_view(['GET', 'POST'])
def ask_view(request):
    if request.method == 'GET':
        return JsonResponse({"message": "CSRF cookie set"})
    elif request.method == 'POST':
        try:
            question = request.data.get("question")

            if not question:
                return JsonResponse({"error": "Missing 'question' field."}, status=400)

            answer = ask_question(question)
            return JsonResponse({"question": question, "answer": answer})
        except Exception as e:
            logging.error("Error occurred while processing the request.")
            logging.error(traceback.format_exc()) 
            return JsonResponse({"error": "An error occurred", "details": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only POST method allowed."}, status=405)

def ask_question(query):
    print(query)
    A = query_json(query)

    context = f"Q: {query},"
    for i in range(1):
        context += f"A: {A[i]},"
        # print(A[i])

    system_prompt = "You are an AI-powered customer service assistant trained to answer questions specifically about refrigerators and dishwashers. If a customer asks for advice on selecting the right product, recommend one or two options with high customer ratings.If a customer asks about instruction on certain product part, read the product page and try to find the useful information. If a customer wants to purchase a product, provide them with the direct link to that product.If a customer asks for details about a product you don't have information on, direct them to the product's webpage.Always keep your responses precise, focused, helpful.If customers want to track their orders, ask them to go to 'https://www.partselect.com/user/self-service/'. \n\n"
    user_prompt = f"{system_prompt} Known information is as follows:\n{context}\nUser Question:{query}\nPlease respond in clear and concise words:"

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content
