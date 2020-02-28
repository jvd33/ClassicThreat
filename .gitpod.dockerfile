FROM gitpod/workspace-full

# Install Redis.
RUN sudo apt-get update \
 && sudo apt-get install -y \
  redis-server \ 
&& sudo apt-get install -y libsnappy-dev \
 && sudo rm -rf /var/lib/apt/lists/*