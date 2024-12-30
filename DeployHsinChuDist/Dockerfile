FROM python:3.9-slim

WORKDIR /app

# 複製所需檔案
COPY index.html .
COPY script.js .
COPY leftturnbox.json .
COPY labeled_HsinChu ./labeled_HsinChu

# 使用非 root 用戶
RUN useradd -m -r -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# 暴露端口
EXPOSE 8040

# 啟動 Python 的簡單 HTTP 伺服器
CMD ["python", "-m", "http.server", "8040"]