from ipykernel.kernelapp import IPKernelApp
from .kernel import GPKernel 
IPKernelApp.launch_instance(kernel_class=GPKernel)
