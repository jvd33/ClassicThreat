# base image
FROM node:latest

# set working directory
COPY . ./app
WORKDIR /app
# add `/app/node_modules/.bin` to $PATH
ENV PATH /node_modules/.bin:$PATH

# install and cache app dependencies
COPY package.json /app/package.json
RUN ls
RUN npm install
RUN npm install @vue/cli -g

# start app
CMD ["npm", "run", "serve"]