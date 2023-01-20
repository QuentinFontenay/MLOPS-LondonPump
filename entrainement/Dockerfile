FROM alpine:latest
RUN apk update && apk --no-cache --update-cache add python3 py3-pandas py3-pip py3-scikit-learn musl-dev proj-util proj-dev gcc g++
COPY . .
WORKDIR /entrainement
RUN pip install --no-cache-dir -r requirements.txt
RUN echo '*/2 * * * * python3 /entrainement/test.py' > /etc/crontabs/root
CMD ["crond", "-f"]
