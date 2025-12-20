/* SQL PARA POSTGRESQL - CREACION DE LA TABLA perfil_comprador */
create table public.perfil_cliente
(
    numero_wp varchar(15) primary key,
    perfil_usuario TEXT not null,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

alter table perfil_cliente
    owner to /*USUARIO N8N y Evolution Api con acceso a la base de datos en mi caso →*/ docker;