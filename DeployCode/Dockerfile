FROM python:3.9-slim

WORKDIR /app

# 複製所需檔案
COPY index.html .
COPY script.js .
COPY answer.json .
COPY detected.json .
COPY data.json .
COPY LeftTurnBoxPhoto_allpoint ./LeftTurnBoxPhoto_allpoint
COPY LeftTurnBoxPhoto_answer ./LeftTurnBoxPhoto_answer
COPY LeftTurnBoxPhoto_detected ./LeftTurnBoxPhoto_detected

# 使用非 root 用戶
RUN useradd -m -r -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# 暴露端口
EXPOSE 8038

# 啟動 Python 的簡單 HTTP 伺服器
CMD ["python", "-m", "http.server", "8038"]