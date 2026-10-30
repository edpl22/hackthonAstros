# Decisões

| Data | Decisão | Motivo |
| --- | --- | --- |
| 2026-10-30 | Trabalhar por etapas, com aprovação do usuário ao fim de cada uma | Pedido do usuário: seguir gradualmente |
| 2026-10-30 | O M1 foi dividido em 1a (esqueleto + câmera local) e 1b (PyInstaller + Release) | Validar a câmera antes de lidar com o empacotamento, que é onde mais coisa quebra |
| 2026-10-30 | Usar `opencv-contrib-python` no lugar de `opencv-python` | O mediapipe já depende do contrib; ter os dois instala dois `cv2` conflitantes |
| 2026-10-30 | Criar `requirements-dev.txt` (inclui `requirements.txt` + ruff/pytest/pytest-qt) | O CI precisa das ferramentas de teste e o PyInstaller precisa só das dependências de execução |
| 2026-10-30 | `QT_QPA_PLATFORM=offscreen` definido também em `tests/conftest.py` | Os testes rodam iguais no CI e no Windows local, sem abrir janelas |
