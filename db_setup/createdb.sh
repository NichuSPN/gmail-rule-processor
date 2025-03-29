psql postgres <<EOF

create role username with login superuser password 'password';

drop database if exists googledb;
create database googledb with owner username;

EOF

psql googledb -U username -h localhost -p 5432 -f init.sql