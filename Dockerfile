FROM python
WORKDIR /
COPY app.py /
COPY req.txt /
RUN pip install -r req.txt
CMD [ "python", "app.py", "--port", "80"]
EXPOSE 5000