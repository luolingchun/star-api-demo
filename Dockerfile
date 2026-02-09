FROM python:3.14-slim-trixie

LABEL author="LLC"

# 使用上海时区
ENV TZ=Asia/Shanghai

# 拷贝依赖包文件
COPY pyproject.toml /tmp/pyproject.toml

# 基础环境安装
RUN \
    set -ex && \
    echo "Types: deb" > /etc/apt/sources.list.d/debian.sources && \
    echo "URIs: https://mirrors.tuna.tsinghua.edu.cn/debian">> /etc/apt/sources.list.d/debian.sources  && \
    echo "Suites: trixie trixie-updates trixie-backports">> /etc/apt/sources.list.d/debian.sources  && \
    echo "Components: main contrib non-free non-free-firmware">> /etc/apt/sources.list.d/debian.sources  && \
    echo "Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg">> /etc/apt/sources.list.d/debian.sources  && \
    \
    apt-get update && \
    apt-get install -y gcc python3-dev --no-install-recommends && \
    \
    pip install uv -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    uv pip install --system -r /tmp/pyproject.toml -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    \
    echo_supervisord_conf > /etc/supervisord.conf && \
    echo "[include]" >> /etc/supervisord.conf && \
    echo "files = /etc/supervisord.d/*.ini" >> /etc/supervisord.conf && \
    \
    apt-get purge -y gcc  python3-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf ~/.cache/pip/*


# 解决中文环境问题（Debian）
RUN apt-get update && \
    apt-get install -y locales && \
    sed -i '/zh_CN.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen zh_CN.UTF-8 && \
    update-locale LANG=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8

# 解决中文环境问题（ubuntu）
#RUN apt-get update && \
#    apt-get install -y language-pack-zh-hans  && \
#    locale-gen zh_CN.UTF-8 && update-locale LANG=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8

ENV LANG='zh_CN.UTF-8'
ENV LANGUAGE='zh_CN:zh:en_US:en'
ENV LC_ALL='zh_CN.UTF-8'

# 工作空间
WORKDIR /work/src

# 添加pythonpath
ENV PYTHONPATH=/work/src

# 程序部署
COPY conf/supervisor.ini /etc/supervisord.d/supervisor.ini
COPY scripts /work/scripts
COPY src /work/src


ENTRYPOINT ["supervisord", "-n","-c", "/etc/supervisord.conf"]