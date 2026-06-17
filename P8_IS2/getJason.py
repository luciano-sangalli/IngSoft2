"""
getJason.py - Sistema automatizado de pagos con selección balanceada de cuentas.

Versión: 1.2
Autor: TP8 - Ingeniería de Software II
Descripción:
    Este módulo implementa un sistema de pagos automatizado que selecciona
    la cuenta bancaria adecuada en base al saldo disponible y distribución
    balanceada. Utiliza los patrones Singleton, Chain of Responsibility e Iterator.
"""

import json
import sys


# =============================================================================
# PATRÓN SINGLETON - Gestor de tokens/claves bancarias
# =============================================================================

class TokenManager:
    """
    Clase Singleton que gestiona la relación entre tokens (bancos) y sus claves.

    Garantiza una única instancia durante toda la ejecución del programa.
    Lee la configuración desde un archivo JSON (sitedata.json).
    """

    _instance = None
    _initialized = False  # declarado aqui para satisfacer pylint

    def __new__(cls, json_file="sitedata.json"):  # pylint: disable=unused-argument
        """Crea o retorna la instancia única del TokenManager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False  # pylint: disable=protected-access
        return cls._instance

    def __init__(self, json_file="sitedata.json"):
        """
        Inicializa el TokenManager cargando datos desde el archivo JSON.

        Args:
            json_file (str): Ruta al archivo JSON con los tokens y claves.
        """
        if self._initialized:  # type: ignore[has-type]
            return
        self._data = {}
        self._load(json_file)
        self._initialized = True

    def _load(self, json_file):
        """
        Carga el archivo JSON con la información de tokens y claves.

        Args:
            json_file (str): Ruta al archivo JSON.

        Raises:
            FileNotFoundError: Si el archivo no existe.
            json.JSONDecodeError: Si el archivo no es JSON válido.
        """
        with open(json_file, "r", encoding="utf-8") as file:
            self._data = json.loads(file.read())

    def get_key(self, token_name):
        """
        Retorna la clave asociada a un token (banco).

        Args:
            token_name (str): Nombre del token a consultar.

        Returns:
            str: Clave correspondiente al token, o None si no existe.
        """
        return self._data.get(token_name)

    def get_all_tokens(self):
        """
        Retorna la lista de todos los tokens disponibles.

        Returns:
            list: Lista de nombres de tokens.
        """
        return list(self._data.keys())


# =============================================================================
# PATRÓN CHAIN OF RESPONSIBILITY - Cuentas bancarias
# =============================================================================

class BankAccount:
    """
    Clase que representa una cuenta bancaria dentro de la cadena de comando.

    Cada cuenta puede procesar un pago o pasarlo al siguiente eslabón
    de la cadena si no tiene saldo suficiente.
    """

    def __init__(self, token_name, initial_balance):
        """
        Inicializa la cuenta bancaria.

        Args:
            token_name (str): Token identificador del banco.
            initial_balance (float): Saldo inicial de la cuenta.
        """
        self._token = token_name
        self._balance = initial_balance
        self._next_account = None
        self._payments = []
        token_mgr = TokenManager()
        self._key = token_mgr.get_key(token_name)

    def set_next(self, account):
        """
        Establece el siguiente eslabón en la cadena.

        Args:
            account (BankAccount): Siguiente cuenta en la cadena.

        Returns:
            BankAccount: La cuenta pasada como argumento (para encadenamiento fluido).
        """
        self._next_account = account
        return account

    def handle_payment(self, order_number, amount):
        """
        Intenta procesar un pago. Si no tiene saldo, lo pasa al siguiente.

        Args:
            order_number (int): Número de pedido.
            amount (float): Monto del pago.

        Returns:
            bool: True si el pago fue procesado, False si ninguna cuenta pudo procesarlo.
        """
        if self._balance >= amount:
            self._balance -= amount
            record = {
                "order": order_number,
                "token": self._token,
                "key": self._key,
                "amount": amount,
                "balance_after": self._balance,
            }
            self._payments.append(record)
            print(
                f"  Pedido #{order_number} | Token: {self._token} "
                f"| Monto: ${amount:.2f} | Saldo restante: ${self._balance:.2f}"
            )
            return True

        if self._next_account:
            return self._next_account.handle_payment(order_number, amount)

        print(f"  Pedido #{order_number}: Sin fondos suficientes en ninguna cuenta.")
        return False

    def get_payments(self):
        """
        Retorna la lista de pagos realizados por esta cuenta.

        Returns:
            list: Lista de registros de pagos.
        """
        return self._payments

    def get_token(self):
        """
        Retorna el nombre del token de esta cuenta.

        Returns:
            str: Nombre del token.
        """
        return self._token

    def get_balance(self):
        """
        Retorna el saldo actual de la cuenta.

        Returns:
            float: Saldo disponible.
        """
        return self._balance


# =============================================================================
# PATRÓN ITERATOR - Listado de pagos
# =============================================================================

class PaymentIterator:
    """
    Iterador que recorre todos los pagos en orden cronológico.

    Implementa el protocolo iterator de Python (__iter__ y __next__).
    """

    def __init__(self, payments):
        """
        Inicializa el iterador con la lista de pagos.

        Args:
            payments (list): Lista de registros de pago ordenados cronológicamente.
        """
        self._payments = payments
        self._index = 0

    def __iter__(self):
        """Retorna el propio iterador."""
        return self

    def __next__(self):
        """
        Retorna el siguiente pago.

        Returns:
            dict: Registro del siguiente pago.

        Raises:
            StopIteration: Cuando no hay más pagos.
        """
        if self._index >= len(self._payments):
            raise StopIteration
        payment = self._payments[self._index]
        self._index += 1
        return payment


# =============================================================================
# CLASE PRINCIPAL - Procesador de pagos
# =============================================================================

class PaymentProcessor:
    """
    Procesador central de pagos que coordina la cadena de cuentas bancarias.

    Gestiona la selección automática y balanceada de cuentas para cada pago.
    """

    VERSION = "1.2"

    def __init__(self, json_file="sitedata.json"):
        """
        Inicializa el procesador configurando las cuentas y la cadena.

        Args:
            json_file (str): Ruta al archivo JSON con datos de tokens.
        """
        TokenManager(json_file)

        self._account1 = BankAccount("token1", 1000.0)
        self._account2 = BankAccount("token2", 2000.0)

        # Construir la cadena: token1 -> token2
        self._account1.set_next(self._account2)

        # Cabeza alternante para distribución balanceada
        self._current_head = self._account1
        self._all_payments = []
        self._order_counter = 0

    def _alternate_head(self):
        """Alterna la cabeza de la cadena para distribuir pagos balanceadamente."""
        if self._current_head == self._account1:
            self._current_head = self._account2
            self._account2.set_next(self._account1)
        else:
            self._current_head = self._account1
            self._account1.set_next(self._account2)

    def request_payment(self, amount):
        """
        Solicita el procesamiento de un pago por el monto indicado.

        La cuenta se selecciona automáticamente de forma balanceada.
        Si la cuenta preferida no tiene fondos, se intenta con la siguiente.

        Args:
            amount (float): Monto del pago a realizar.

        Returns:
            bool: True si el pago fue exitoso, False en caso contrario.
        """
        self._order_counter += 1
        order_number = self._order_counter

        # Capturar el estado de pagos ANTES para detectar cuál cuenta procesó
        prev_count1 = len(self._account1.get_payments())
        prev_count2 = len(self._account2.get_payments())

        success = self._current_head.handle_payment(order_number, amount)

        if success:
            # Detectar qué cuenta procesó el pago y registrarlo globalmente
            new_count1 = len(self._account1.get_payments())
            new_count2 = len(self._account2.get_payments())

            if new_count1 > prev_count1:
                self._all_payments.append(self._account1.get_payments()[-1])
            elif new_count2 > prev_count2:
                self._all_payments.append(self._account2.get_payments()[-1])

            self._alternate_head()

        return success

    def list_payments(self):
        """
        Lista todos los pagos realizados en orden cronológico usando un Iterator.

        Muestra número de pedido, token utilizado y monto de cada pago.
        """
        print("\n" + "=" * 60)
        print("  LISTADO DE PAGOS (orden cronológico)")
        print("=" * 60)

        iterator = PaymentIterator(self._all_payments)
        for idx, payment in enumerate(iterator, start=1):
            print(
                f"  {idx:>2}. Pedido #{payment['order']:>3} | "
                f"Token: {payment['token']:<8} | "
                f"Monto: ${payment['amount']:>8.2f}"
            )

        print("=" * 60)
        print(f"  Total de pagos: {len(self._all_payments)}")
        print(f"  Saldo cuenta token1: ${self._account1.get_balance():.2f}")
        print(f"  Saldo cuenta token2: ${self._account2.get_balance():.2f}")
        print("=" * 60)


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

def main():
    """
    Función principal: ejecuta una demostración del sistema de pagos.

    Acepta opcionalmente la ruta al archivo JSON como argumento de línea de comandos.
    Por defecto utiliza 'sitedata.json'.
    """
    json_file = sys.argv[1] if len(sys.argv) > 1 else "sitedata.json"

    print(f"\nSistema de Pagos Automatizado v{PaymentProcessor.VERSION}")
    print("-" * 60)

    processor = PaymentProcessor(json_file)

    # Realizar pedidos de pago de $500 cada uno
    payment_amount = 500.0
    num_payments = 6

    print(f"\nProcesando {num_payments} pagos de ${payment_amount:.2f}:\n")

    for _ in range(num_payments):
        processor.request_payment(payment_amount)

    # Mostrar listado completo usando el iterador
    processor.list_payments()


if __name__ == "__main__":
    main()