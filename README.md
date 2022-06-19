# Docker/Singularity capabilities for OpenFOAM&reg; + HiSA + PyTorch

## Overview

The Dockerfile in this repository creates an image with [ESI-OpenFOAM](https://openfoam.com/), [HiSA](https://hisa.gitlab.io/) and [PyTorch](https://pytorch.org/) support. The image is currently based on

- Ubuntu 22.04,
- OpenFOAM-v2112,
- HiSA 1.4.6, and
- PyTorch 1.10.2 (only CPU).


OpenFOAM is not compiled from scratch but installed via the package manager ([read more](https://develop.openfoam.com/Development/openfoam/-/wikis/precompiled/debian)). Also for PyTorch, only the pre-compiled C++ part of the library, named *libtorch*, is contained on the image. However, the HiSA package is pulled from the [source](https://gitlab.com/hisa/hisa) and compiled, in which the libraries are installed in `$FOAM_APPBIN` and `$FOAM_LIBBIN` instead of user libraries.

## How to build the images

### Docker
<details>
<summary markdown="spawn"> Click to expand! </summary>
  
  To build a docker image,
  
  ```
  git clone https://github.com/darshan315/OpenFOAM_HiSA_PyTorch.git
  cd OpenFOAM_HiSA_PyTorch
  docker build -t user_name/openfoam_hisa_pytorch:of2112_hisa1.4.6_pt1.10.2_ub22.04 -f Dockerfile .
  ```
  To create a container,
  
  ```
  ./create_openfoam_container.sh
  ```
  
  To start the container and use interactively,
  
  ```
  ./start_openfoam.sh
  ```
  
</details>
  
  
### Singularity
<details>
<summary markdown="spawn"> Click to expand! </summary>
  
  To build the image (.sif),
  ```
  sudo singularity build of2112_hisa1.4.6_pt1.10.2_ub22.04.sif Singularity.def
  ```
  To use the container interactively,
  ```
  singularity shell of2112_hisa1.4.6_pt1.10.2_ub22.04.sif
  ```
  To use the image non-interactively and run the application,
  ```
  singularity run of2112_hisa1.4.6_pt1.10.2_ub22.04.sif [path] [arguments]
  ```
</details> 

## Tests
<details>
<summary markdown="spawn"> Click to expand! </summary>

  The test directory contains the example scripts for OpenFOAM, HiSA, and PyTorch. These examples can be executed to check the correct installation and compilation.

### OpenFOAM:
  + <details>
    <summary markdown="spawn"> Click to expand! </summary>
  
      The test case for OpenFOAM follows [cavity example](https://develop.openfoam.com/Development/openfoam/-/tree/master/tutorials/incompressible/icoFoam/cavity/cavity) given in OpenFoam tutorials. The example can be run from top-level directory of this repository as,

      ```
      # To run the simulation
      singularity run of2112_hisa1.4.6_pt1.10.2_ub22.04.sif ./Allrun ./test/cavity/
      # To clean the finished simulation
      singularity run of2112_hisa1.4.6_pt1.10.2_ub22.04.sif ./Allclean ./test/cavity/
      ```
  
    </details>
  
### HiSA
  + <details>
    <summary markdown="spawn"> Click to expand! </summary>
      
      The test case for HiSA follows [rae2822 example](https://gitlab.com/hisa/hisa/-/tree/master/examples/rae2822) given in HiSA examples. The example can be run from top-level directory of this repository as,    
  
      ```
      # To generate the mesh
      singularity run of2112_hisa1.4.6_pt1.10.2_ub22.04.sif ./setupMesh ./test/rae2822/
      # To run the simulation
      singularity run of2112_hisa1.4.6_pt1.10.2_ub22.04.sif ./runSim ./test/rae2822/
      # To clean the mesh
      singularity run of2112_hisa1.4.6_pt1.10.2_ub22.04.sif ./cleanMesh ./test/rae2822/
      # To clean the finished simulation
      singularity run of2112_hisa1.4.6_pt1.10.2_ub22.04.sif ./cleanSim ./test/rae2822/
      ```
  
    </details>
  
 ### PyTorch

+ <details>
  <summary markdown="spawn"> Click to expand! </summary>

    From top-level directory of this repository, you can build and run *tensorCreation* as follows:

    ```
    # build
    singularity run of2112_hisa1.4.6_pt1.10.2_ub22.04.sif wmake test/tensorCreation/
    # run
    singularity run of2112_hisa1.4.6_pt1.10.2_ub22.04.sif ./tensorCreation test/tensorCreation/
    # clean
    singularity run of2112_hisa1.4.6_pt1.10.2_ub22.04.sif wclean test/tensorCreation/
    ```
    Alternatively, one can also define scripts, which are then executed by Singularity. For example, to build and run the second example, *simpleMLP*, run the *compileAndRun.sh* script:

    ```
    singularity run of2112_hisa1.4.6_pt1.10.2_ub22.04.sif ./compileAndRun.sh test/simpleMLP/
    ```

  </details>
  
</details> 

**For more Information, see [1](https://ml-cfd.com/openfoam/pytorch/docker/2020/12/29/running-pytorch-models-in-openfoam.html), [2](https://openfoam.com/), [3](https://hisa.gitlab.io/), [4](https://pytorch.org/), [5](https://www.docker.com/), [6](https://docs.sylabs.io/guides/3.0/user-guide/index.html#).**
