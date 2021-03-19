FROM 172.16.11.205:8001/ai-ocr/bankcard-ocr:0a0eca6.master.27
ENV LANG C.UTF-8

ENV LD_LIBRARY_PATH=/usr/local/lib/python3.7/dist-packages/paddle/libs/:$LD_LIBRARY_PATH
# 将工作目录设置为 /app
WORKDIR /app

# 将当前目录内容复制到位于 /app 中的容器中
ADD . /app
CMD ["python","app.py"]