# As root:
sudo usermod -aG docker $USER

# Then reload your group membership:
# Either log out & back in, or simply run:
newgrp docker

