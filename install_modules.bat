for /D %%d in (netforce_*) do (cd %%d & python setup.py develop & cd ..)
