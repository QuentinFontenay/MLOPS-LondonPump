FROM alpine:latest
RUN apk update && apk --no-cache --update-cache add python3 py3-pandas py3-pip py3-scikit-learn
COPY . .
WORKDIR /api
RUN pip install --no-cache-dir -r requirements.txt
CMD uvicorn main:api
