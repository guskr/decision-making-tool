# Decision-Making tool Development Notes
t

1. Reiniciar PC
2. Instalar Anaconda
3. Criar um novo enviroment
4. dar conda init powershell
5. Seguir as instrucoes abaixo

python -m ipykernel install --user


# Preparing the enviroment

Clone base enviroment 

conda create --name decision-making-env-tool --clone base



```bash
conda create --name decision-making-env-tool
conda activate decision-making-env-tool 
```
# Install dependencies
```bash
# Install dependencies

conda install -c conda-forge nb_conda_kernels
conda install -c conda-forge jupyter
conda install -c conda-forge jupyterlab
conda install -c conda-forge nodejs
conda install -c conda-forge voila
conda install -c conda-forge voila-gridstack
pip install plotly
pip install dash
pip install jupyter-dash

conda install -c conda-forge jupyter-dash (ja instala o dash e o plotly)
conda install -c conda-forge dask-labextension
https://github.com/dask/dask-labextension
pip install dask_labextension (https://morioh.com/p/d56c5d2b8c41)


conda install mamba -n base -c conda-forge
mamba install -c conda-forge dash


conda install dash



conda install -c conda-forge plotly 
```
# Update Conda
conda update -n base conda
conda update --all


# Deleting the enviroment
```bash
conda env list

conda deactivate

conda remove --name corrupted_env --all
```

# Conda list packages
conda env list
# conda clone and rename env
conda deactivate

Step 3: Clone the Conda Environment
The simplest command to clone is as follows:

conda create --name cloned_env --clone original_env


conda create --name decision-making-env-tool --clone base
conda create --name decision-making-dash --clone decision-making

# Create new enviroment 

create a new environment using that specification.

conda create --name myenv --file spec-file.txt

# Create spec list 
conda list --explicit > spec-file.txt

conda create --name decision-making-env --file spec-file.txt

# conda delete env
conda env remove -n corrupted_env

# Conda update
conda update

# npm
```bash
npm install @tupilabs/vue-lumino
```




# References
https://github.com/tupilabs/vue-lumino
https://jupyter.org/ - interactive python command line/shell 
https://github.com/studyhub-co/jupyterlab_vue
https://github.com/jupyterlab/lumino  - dashboard extension
https://github.com/tupilabs/vue-lumino   - widgets extension
https://github.com/studyhub-co/jupyterlab_vue – simple coding example
http://jupyter-dashboards-layout.readthedocs.io/en/latest/using.html – extension for changing layout


------------------
# Install dependencies
conda install -c conda-forge nb_conda_kernels # access kernels on jupyterlab
conda install -c conda-forge dash # web interactive graphics
conda install -c conda-forge voila # conversion to web
conda install -c conda-forge plotly # graphics
conda install -c conda-forge nodejs # dependency of jupyter-dash
conda install -c conda-forge jupyter-dash # dash support for jupyter
conda install -c conda-forge jupyterlab voila-gridstack # grid laylout





- Testar dask dashboard to jupyterlab

- Assistir https://youtu.be/owSGVOov9pQ

- testar o binder
- https://github.com/dask/dask-labextension

- criar o seguinne app:
	https://youtu.be/dgxYA-9bTGE

- Guide for project design

https://the-turing-way.netlify.app/project-design/project-design.html


conda list 

pip remove dask-labextension
conda update
conda install -c conda-forge -c plotly jupyter-dash
jupyter lab build

https://ipydrawio.readthedocs.io/en/stable/



-----------
Estudar Aref Neto - Capítulo 1
Estudar Português capitulo 1 do Napoleao
Latim estudar capitulo 1 do Napoleao
Alemao - Capítulo 1
Frances - Capítulo 1
Fisica Alonso Finn - Capítulo 1
Quimica - Capítulo 1
Ler Camoes e Ver Overleaf


https://sjdaccountancy.com/resources/ir35/outside-ir35/