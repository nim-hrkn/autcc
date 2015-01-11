echo "update sio2 set dbstatus='submitted',execstatus='finished' where dbstatus='submitted' and execstatus='idle';" | sqlite3  sio2data.sqlite3
