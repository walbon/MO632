#!/bin/bash

function get_power(){

        echo -ne " { \"timestamp\": \"$(date +%Y%m%d-%T.%N)\" \
                $(dbus-send --system --print-reply --dest=org.open_power.OCC.Control \
                /xyz/openbmc_project/sensors \
                org.freedesktop.DBus.ObjectManager.GetManagedObjects | \
                grep -e "object path" -e variant | \
                grep -v -e 'inf$' -e 'boolean true' -e string -e array | \
                sed '    s/ *object path *\([^\s]*\)/\1/' | \
                sed 's/ *variant *double //g' | \
                awk 'NR%2{printf "%s \t",$0;next;}1' | sort - | \
cut -d "/" -f6  | tr -d "\t" | \
                sed -e "s;\(.*\)\"\ *\([^\ \t]*\);,\"\1\": \2;g") }\n"
}


while ( true ); 
do
        get_power

        sleep 0.05 # sampling of 20Hz
done
