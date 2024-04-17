#!/bin/bash

function create_vault_script
{
    VAULT_SCRIPT=$1
    cat <<EOF >>$VAULT_SCRIPT
    #!/bin/bash
    cd /
    readonly LOCK_FILE="/var/lib/data/ace/dropbox/vault/.lock"
    if [[ -f "\$LOCK_FILE" ]]; then
        exec 200>\$LOCK_FILE
        if ! timeout 30s flock -x 200; then
            echo "Failed to aquire vault flock, achiving anyway..."
        else
            echo "Lock aquired, achiving..."
        fi
    else
        echo "No lock found, achiving anyway..."
    fi

    rm -f    /var/lib/data/ace/dropbox/vault-snapshot.tgz
    tar -czf /var/lib/data/ace/dropbox/vault-snapshot.tgz /var/lib/data/ace/dropbox/vault /var/log /var/run/log /var/lib/data/acr /cache/recovery || true
    ls -l    /var/lib/data/ace/dropbox/vault-snapshot.tgz

    # Exclusive flock on fd 200 is released when this script exits
EOF
# EOF must not be indented, and have no trailing whitespace
    chmod +x $VAULT_SCRIPT
}

function device_dump
{
    DIRBASEDEV=${TIME}_log
    dev_path[$2]=$DIRBASEDEV

    DIRBASEDEV=$DIRBASE/$DIRBASEDEV
    DEVREADME=$DIRBASEDEV/README
    SCRLOGCUR=$DIRBASEDEV/adb_errors.log
    DRPBXLOG=$DIRBASEDEV/dropbox_extract.log

    mkdir -p $DIRBASEDEV

    echo "=============================="  > $DEVREADME
    echo "Date & Time     $TIME" >> $DEVREADME
    echo "Base folder:    system_log" >> $DEVREADME
    echo "Script ver.:    $VER" >> $DEVREADME
    echo "User:           $USER($UID)" >> $DEVREADME
    echo "Build No:       $BUILDNO" >> $DEVREADME
    echo "Build Type:     $BUILDTYPE" >> $DEVREADME
    echo "Build Product:  $BUILDPRODUCT" >> $DEVREADME
    echo "Permissions:    $dev_permission" >> $DEVREADME
    echo "=============================="  >> $DEVREADME
    echo "" >> $DEVREADME

    echo "OS Version Info..."
    cp -r /usr/lib/os-release $DIRBASEDEV/os-release

    # Change the working directory
    WORK_DIR=$(dirname $(pwd))
    WORK_DIR=`basename $WORK_DIR`
    WORK_DIR=${WORK_DIR##*-}

    echo "Getting dropbox..."
    create_vault_script "vault_script.sh"
    
    cp -r vault_script.sh /tmp 1>> $SCRLOGCUR 2>&1
    bash /tmp/vault_script.sh 1>> $SCRLOGCUR 2>&1

    cp -r /var/lib/data/ace/dropbox/vault-snapshot.tgz $DIRBASEDEV/vault-snapshot.tgz 1>> $SCRLOGCUR 2>&1
    ls -l $DIRBASEDEV/vault-snapshot.tgz 1>> $SCRLOGCUR 2>&1
    rm -rf /var/lib/data/ace/dropbox/vault-snapshot.tgz 1>> $SCRLOGCUR 2>&1

    mkdir $DIRBASEDEV/dropbox
    mkdir $DIRBASEDEV/unity_log

    cp -r /home/app_user/packages/* $DIRBASEDEV/unity_log 2>&1
    tar -xvf $DIRBASEDEV/vault-snapshot.tgz -C $DIRBASEDEV/dropbox 1>> $DRPBXLOG 2>&1 || true
    gunzip -r $DIRBASEDEV/dropbox 1>> $DRPBXLOG 2>&1 || true
    rm -rf $DIRBASEDEV/dropbox/var/log/README 2>&1
    rm -rf $DIRBASEDEV/vault-snapshot.tgz 2>&1

    rm -rf ./vault_script.sh
    rm -rf /tmp/vault_script.sh 1>> $SCRLOGCUR 2>&1

    echo "Done!"

    sleep 1
}

function mode1_get_logs
{
    TIME=`date +%Y%m%d_%H%M`
    DIRBASE=`printf system_log`
    README=$DIRBASE/README;
    OSVER=`lsb_release -a 2>/dev/null | grep Description | sed -e "s/Description:[ \t]//"`
    DIRSUM=analysis

    make_base;
    device_dump;
}

function make_base
{
    mkdir -p $DIRBASE
    if [ "$?" -ne "0" ]; then echo "Can't make base folder: $DIRBASE"; exit -1; fi

    echo "=============================="  | tee -a $README
    echo "Date & Time  $TIME" | tee -a $README
    echo "Base folder: $DIRBASE" | tee -a $README
    echo "OS:          $OSVER" | tee -a $README
    echo "Bash ver.:   $BASH_VERSION" | tee -a $README
    echo "User:        $USER($UID)" | tee -a $README
}

mode1_get_logs;