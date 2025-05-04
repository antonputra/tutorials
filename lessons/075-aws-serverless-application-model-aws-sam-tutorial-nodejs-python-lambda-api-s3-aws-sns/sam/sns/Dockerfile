FROM public.ecr.aws/lambda/python:3.8

COPY function.py requirements.txt ./

RUN python3.8 -m pip install -r requirements.txt -t .

CMD ["function.lambda_handler"]
