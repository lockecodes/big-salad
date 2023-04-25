# Big Salad

### "It's a salad, only bigger, with lots of stuff in it."

This repository is a collection of general-purpose tooling designed to make daily tasks easier. The name "Big Salad" is
a playful reference to the Seinfeld episode where Elaine famously orders a "big salad" – a larger and more varied
version of a salad, just like this repository is a larger and more feature-packed collection of tools.

## Overview

Big Salad provides a variety of tools bundled together in one repository. Whether you're looking to automate tasks,
improve workflows, or explore some utility scripts, Big Salad has a little bit of everything.

## Quick Installation

The best way of utilizing this script is to actually install it using the container-cli tooling. Follow these steps:

# Installation Instructions

## Step 1: Download Release

1. Navigate to the [Container CLI Releases](https://gitlab.com/locke-codes/container-cli/-/releases).
2. Download the appropriate release for your operating system.

---

## Step 2: Extract and Install

1. Open a terminal and navigate to the directory where the release file is downloaded.
2. Extract the downloaded tar file using the following command:
   ```bash
   tar -xvf ~/Downloads/container-cli_Linux_x86_64.tar.gz
   ```

3. Execute the binary file to install `container-cli`:
   ```bash
   ./container-cli install
   ```

---

## Step 3: Install Big Salad

```bash
ccli project install -name big-salad -url ssh://git@gitlab.com/slocke716/big-salad.git -dest /home/user/projects -command bs
```

## Step 4: Onces installed run Big Salad
```shell
big-salad format yaml test.yaml
```

## What's Inside?

Big Salad is a collection of scripts and tooling that spans multiple domains and use cases. It's designed to be modular
and versatile, offering something for everyone. The individual tools are loosely tied together to cover diverse
scenarios – the perfect toolkit for making your life easier.
That being said, this was built for myself to keep track of tooling that I use for reference and usage on personal projects.

## Usage

Once installed, dive into the collection and explore the tools available. Each script or tool will typically have its
own usage instructions or comments for guidance.

## Contribution

Contributions are welcome to make the Big Salad even bigger and better! If you have any suggestions, fixes, or new tools
to add, feel free to submit a merge request.

---

Enjoy your Big Salad!