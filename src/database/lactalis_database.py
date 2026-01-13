"""
Base de datos SQLite para Lactalis Ventas
Gestiona materiales y clientes con validaciones automáticas
"""

import sqlite3
import logging
import os
from typing import List, Dict, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class LactalisDatabase:
    """
    Gestor de base de datos SQLite para Lactalis Ventas

    TABLAS:
    1. materiales: CODIGO, DESCRIPCION, SOCIEDAD
    2. clientes: cod_padre, nombre_codigo_padre, nit
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Inicializa la conexión a la base de datos

        Args:
            db_path: Ruta al archivo de base de datos. Si es None, usa la ruta por defecto.
        """
        try:
            if db_path is None:
                # Determinar la ruta por defecto según el sistema operativo
                if os.name == 'nt':  # Windows
                    app_data = os.getenv('APPDATA')
                    if app_data:
                        base_dir = Path(app_data) / 'BogotaSAE' / 'database'
                    else:
                        base_dir = Path.cwd() / 'database'
                else:  # Linux/Mac
                    base_dir = Path.cwd() / 'database'

                logger.info(f"Creando directorio de base de datos: {base_dir}")
                base_dir.mkdir(parents=True, exist_ok=True)
                db_path = str(base_dir / 'lactalis_ventas.db')

            self.db_path = db_path
            logger.info(f"Ruta de base de datos: {self.db_path}")

            self.conn = None
            self._conectar()
            self._crear_tablas()

            logger.info("Base de datos inicializada correctamente")
        except Exception as e:
            logger.error(f"Error en __init__ de LactalisDatabase: {str(e)}", exc_info=True)
            raise

    def _conectar(self):
        """Conecta a la base de datos SQLite"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Conectado a base de datos: {self.db_path}")
        except Exception as e:
            logger.error(f"Error conectando a base de datos: {str(e)}")
            raise

    def _crear_tablas(self):
        """Crea las tablas si no existen"""
        try:
            cursor = self.conn.cursor()

            # Tabla de materiales
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS materiales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT NOT NULL,
                    descripcion TEXT NOT NULL,
                    sociedad TEXT NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(codigo, sociedad)
                )
            """)

            # Índice para búsqueda rápida de materiales
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_materiales_codigo
                ON materiales(codigo)
            """)

            # Tabla de clientes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cod_padre TEXT NOT NULL,
                    nombre_codigo_padre TEXT NOT NULL,
                    nit TEXT,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(cod_padre)
                )
            """)

            # Índice para búsqueda rápida de clientes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_clientes_cod_padre
                ON clientes(cod_padre)
            """)

            self.conn.commit()
            logger.info("Tablas creadas/verificadas exitosamente")

        except Exception as e:
            logger.error(f"Error creando tablas: {str(e)}")
            raise

    # ==================== MÉTODOS PARA MATERIALES ====================

    def importar_materiales(self, materiales: List[Dict]) -> Tuple[int, int, int]:
        """
        Importa materiales desde una lista de diccionarios
        Solo guarda los materiales nuevos (no duplica)

        Args:
            materiales: Lista de diccionarios con keys: codigo, descripcion, sociedad

        Returns:
            Tupla (nuevos, existentes, errores)
        """
        nuevos = 0
        existentes = 0
        errores = 0

        cursor = self.conn.cursor()

        for material in materiales:
            try:
                codigo = str(material.get('codigo', '')).strip()
                descripcion = str(material.get('descripcion', '')).strip()
                sociedad = str(material.get('sociedad', '')).strip()

                # Validar campos requeridos
                if not codigo or not descripcion or not sociedad:
                    logger.warning(f"Material incompleto: {material}")
                    errores += 1
                    continue

                # Verificar si ya existe
                cursor.execute("""
                    SELECT id FROM materiales
                    WHERE codigo = ? AND sociedad = ?
                """, (codigo, sociedad))

                if cursor.fetchone():
                    existentes += 1
                    logger.debug(f"Material ya existe: {codigo} - {sociedad}")
                else:
                    # Insertar nuevo material
                    cursor.execute("""
                        INSERT INTO materiales (codigo, descripcion, sociedad)
                        VALUES (?, ?, ?)
                    """, (codigo, descripcion, sociedad))
                    nuevos += 1
                    logger.debug(f"Material insertado: {codigo} - {descripcion}")

            except Exception as e:
                logger.error(f"Error importando material {material}: {str(e)}")
                errores += 1

        self.conn.commit()
        logger.info(f"Importación materiales: {nuevos} nuevos, {existentes} existentes, {errores} errores")

        return nuevos, existentes, errores

    def validar_material(self, codigo: str, sociedad: str) -> bool:
        """
        Valida si un material existe en la base de datos

        Args:
            codigo: Código del material
            sociedad: Sociedad del material

        Returns:
            True si existe, False si no existe
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id FROM materiales
                WHERE codigo = ? AND sociedad = ?
            """, (codigo.strip(), sociedad.strip()))

            return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error validando material: {str(e)}")
            return False

    def obtener_material(self, codigo: str, sociedad: str) -> Optional[Dict]:
        """
        Obtiene los datos de un material

        Args:
            codigo: Código del material
            sociedad: Sociedad del material

        Returns:
            Diccionario con datos del material o None si no existe
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT codigo, descripcion, sociedad, fecha_creacion
                FROM materiales
                WHERE codigo = ? AND sociedad = ?
            """, (codigo.strip(), sociedad.strip()))

            row = cursor.fetchone()
            if row:
                return {
                    'codigo': row['codigo'],
                    'descripcion': row['descripcion'],
                    'sociedad': row['sociedad'],
                    'fecha_creacion': row['fecha_creacion']
                }
            return None
        except Exception as e:
            logger.error(f"Error obteniendo material: {str(e)}")
            return None

    def contar_materiales(self) -> int:
        """Cuenta el total de materiales en la base de datos"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM materiales")
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error contando materiales: {str(e)}")
            return 0

    def listar_materiales(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Lista materiales con paginación

        Args:
            limit: Número máximo de resultados
            offset: Número de resultados a saltar

        Returns:
            Lista de diccionarios con materiales
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT codigo, descripcion, sociedad, fecha_creacion
                FROM materiales
                ORDER BY fecha_creacion DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))

            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error listando materiales: {str(e)}")
            return []

    # ==================== MÉTODOS PARA CLIENTES ====================

    def importar_clientes(self, clientes: List[Dict]) -> Tuple[int, int, int]:
        """
        Importa clientes desde una lista de diccionarios
        Solo guarda los clientes nuevos (no duplica)

        Regla especial: Si en el campo NIT dice "no nit", no se registra el cliente

        Args:
            clientes: Lista de diccionarios con keys: cod_padre, nombre_codigo_padre, nit

        Returns:
            Tupla (nuevos, existentes, errores)
        """
        nuevos = 0
        existentes = 0
        errores = 0

        cursor = self.conn.cursor()

        for cliente in clientes:
            try:
                cod_padre = str(cliente.get('cod_padre', '')).strip()
                nombre = str(cliente.get('nombre_codigo_padre', '')).strip()
                nit = str(cliente.get('nit', '')).strip()

                # Validar campos requeridos
                if not cod_padre or not nombre:
                    logger.warning(f"Cliente incompleto: {cliente}")
                    errores += 1
                    continue

                # REGLA ESPECIAL: Si dice "no nit", no registrar
                if nit.lower() in ['no nit', 'nonit', 'sin nit']:
                    logger.info(f"Cliente {cod_padre} no registrado (NIT: {nit})")
                    errores += 1
                    continue

                # Validar que si tiene NIT, sea válido (no vacío)
                nit_final = nit if nit and nit.lower() != 'nit' else None

                # Verificar si ya existe
                cursor.execute("""
                    SELECT id FROM clientes
                    WHERE cod_padre = ?
                """, (cod_padre,))

                if cursor.fetchone():
                    existentes += 1
                    logger.debug(f"Cliente ya existe: {cod_padre}")
                else:
                    # Insertar nuevo cliente
                    cursor.execute("""
                        INSERT INTO clientes (cod_padre, nombre_codigo_padre, nit)
                        VALUES (?, ?, ?)
                    """, (cod_padre, nombre, nit_final))
                    nuevos += 1
                    logger.debug(f"Cliente insertado: {cod_padre} - {nombre}")

            except Exception as e:
                logger.error(f"Error importando cliente {cliente}: {str(e)}")
                errores += 1

        self.conn.commit()
        logger.info(f"Importación clientes: {nuevos} nuevos, {existentes} existentes, {errores} errores")

        return nuevos, existentes, errores

    def validar_cliente(self, nit: str) -> bool:
        """
        Valida si un cliente existe en la base de datos por NIT

        Args:
            nit: NIT del cliente

        Returns:
            True si existe, False si no existe
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id FROM clientes
                WHERE nit = ?
            """, (nit.strip(),))

            return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error validando cliente: {str(e)}")
            return False

    def obtener_cliente(self, cod_padre: str) -> Optional[Dict]:
        """
        Obtiene los datos de un cliente

        Args:
            cod_padre: Código padre del cliente

        Returns:
            Diccionario con datos del cliente o None si no existe
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT cod_padre, nombre_codigo_padre, nit, fecha_creacion
                FROM clientes
                WHERE cod_padre = ?
            """, (cod_padre.strip(),))

            row = cursor.fetchone()
            if row:
                return {
                    'cod_padre': row['cod_padre'],
                    'nombre_codigo_padre': row['nombre_codigo_padre'],
                    'nit': row['nit'],
                    'fecha_creacion': row['fecha_creacion']
                }
            return None
        except Exception as e:
            logger.error(f"Error obteniendo cliente: {str(e)}")
            return None

    def contar_clientes(self) -> int:
        """Cuenta el total de clientes en la base de datos"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM clientes")
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error contando clientes: {str(e)}")
            return 0

    def listar_clientes(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Lista clientes con paginación

        Args:
            limit: Número máximo de resultados
            offset: Número de resultados a saltar

        Returns:
            Lista de diccionarios con clientes
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT cod_padre, nombre_codigo_padre, nit, fecha_creacion
                FROM clientes
                ORDER BY fecha_creacion DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))

            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error listando clientes: {str(e)}")
            return []

    # ==================== MÉTODOS GENERALES ====================

    def cerrar(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()
            logger.info("Conexión a base de datos cerrada")

    def __enter__(self):
        """Context manager enter"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cerrar()
