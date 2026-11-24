FROM python:3.13.18-slim-trixie@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore \
    TIKTOKEN_CACHE_DIR=/opt/tiktoken
WORKDIR /lab
COPY requirements.txt constraints.txt ./
RUN pip install -r requirements.txt -c constraints.txt
# The scripted model counts tokens with tiktoken's o200k_base encoding. Fetch its vocabulary file once, here,
# so that nothing is downloaded when the lab runs. tiktoken checks the file against a hash it carries.
RUN python -c "import tiktoken; print(tiktoken.get_encoding('o200k_base').n_vocab, 'tokens in o200k_base')"
COPY . .
