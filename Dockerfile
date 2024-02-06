FROM python
WORKDIR /
COPY / /
RUN pip install -r req.txt
CMD [ "py", "app.py"]
EXPOSE 5000