# remote_jlab

## commands 

jlab   - start remote session  
sshjup  - connect via ssh 

## ToDo: 
on remote pc
- install tmux 
- make venv with jupiter lab

on local pc: 
- venv for `jup.py`
- alias (jlab + ssh connect)


## Alias

```bash
function jlab() {
    source ~/jup-serv/bin/activate  # path to venv # change 
    python3 ~/remote_jlab/jup.py          
    deactivate
}
```


```bash
alias sshjup="ssh -N -L 8889:127.0.0.1:8889 pc"
```

`pc`  is shortcut for connection via ssh (setup in .ssh/config)
Example: 
```
Host pc
    AddKeysToAgent yes
    UseKeychain yes
    HostName [ip]
    User [user_name]
    PreferredAuthentications publickey
    IdentityFile [path_2_key]
```
