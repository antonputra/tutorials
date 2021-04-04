FROM public.ecr.aws/lambda/python:3.8

COPY app.py requirements.txt ${LAMBDA_TASK_ROOT}/

RUN pip3 install --target ${LAMBDA_TASK_ROOT}/ -r requirements.txt

CMD ["app.lambda_handler"]
