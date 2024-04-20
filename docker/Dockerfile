# 使用するPythonのイメージを指定
FROM python:3.12

# 必要なパッケージのインストール（zipコマンドを含む）
RUN apt-get update && apt-get install -y \
    zip \
    && rm -rf /var/lib/apt/lists/*

# Poetryのインストール
RUN curl -sSL https://install.python-poetry.org | python -

# Poetryのパスの設定
ENV PATH /root/.local/bin:$PATH

# Poetryが仮想環境を生成しないようにする
RUN poetry config virtualenvs.create false

# 作業ディレクトリを設定
WORKDIR /scraping-hub

COPY ./scraping-hub /scraping-hub/

# 依存関係をインストール
RUN poetry install --no-dev

COPY ./docker/entrypoint.sh /entrypoint.sh

# スクリプトに実行権限を付与
RUN chmod +x /entrypoint.sh
