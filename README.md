# gp_kernel

A simple IPython kernel for gp.

It simply writes each cell as temporary file and then reads it with `\r`.


## Installation

You must have [Jupyter](https://jupyter.org/) installed in your system. For example, it comes with
[SageMath](http://www.sagemath.org/).
If are using [SageMath](http://www.sagemath.org/), you can install `gp_kernel` by doing:

```
sage -pip install git+https://github.com/edgarcosta/gp_kernel.git
```

if you are using [Jupyter](https://jupyter.org/) as a standalone, you can install `gp_kernel` by doing

```
pip install git+https://github.com/edgarcosta/gp_kernel.git
```

Consider adding the flag `--user` if you do not have permissions to install it system-wide.



## Credit & Others
Mutatis mutandis [edgarcosta/magma_kernel](https://github.com/edgarcosta/magma_kernel).

Which is based on [takluyver/bash_kernel](https://github.com/takluyver/bash_kernel) and [cgranade/gp_kernel](https://github.com/cgranade/gp_kernel).
Reporting partial output and processing of help requests by returning an appropriate help query URL provided by [nbruin/gp_kernel](https://github.com/nbruin/gp_kernel).

For details of how this works, see the Jupyter docs on
[wrapper kernels](http://jupyter-client.readthedocs.org/en/latest/wrapperkernels.html), and
Pexpect's docs on the [spawn class](https://pexpect.readthedocs.io/en/latest/api/pexpect.html#spawn-class)
