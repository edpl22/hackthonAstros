import os

# Os testes nunca abrem janelas, nem no CI nem na máquina local.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
