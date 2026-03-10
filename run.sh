#!/usr/bin/env bash
# Скрипт для запуска/перезапуска контейнера Receipt_maker

set -e

CONTAINER_NAME="receipt_maker"
IMAGE_NAME="receipt_maker"
PORT=8000
BUILD=false
NO_CACHE=""

usage() {
    echo "Использование: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Команды:"
    echo "  rebuild        Пересобрать образ и запустить контейнер"
    echo ""
    echo "Опции:"
    echo "  -b, --build    Пересобрать образ перед запуском"
    echo "  --no-cache     Полная пересборка образа без кэша Docker"
    echo "  -h, --help     Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0                  # Запуск (перезапуск) контейнера"
    echo "  $0 rebuild          # Пересборка образа и запуск"
    echo "  $0 --build          # То же, что rebuild"
    echo "  $0 --build --no-cache   # Полная пересборка без кэша"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        rebuild)
            BUILD=true
            shift
            ;;
        -b|--build)
            BUILD=true
            shift
            ;;
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Неизвестная опция: $1"
            usage
            exit 1
            ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Останавливаем и удаляем старый контейнер, если есть
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Останавливаем контейнер ${CONTAINER_NAME}..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME"
    echo "Контейнер удалён."
fi

if [ "$BUILD" = true ]; then
    echo "Пересборка образа ${IMAGE_NAME}..."
    docker build $NO_CACHE -t "$IMAGE_NAME" .
    echo "Образ собран."
fi

# Если образа нет — собираем
if ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
    echo "Образ не найден. Собираем..."
    docker build $NO_CACHE -t "$IMAGE_NAME" .
fi

echo "Запуск контейнера ${CONTAINER_NAME} на порту ${PORT}..."
docker run -d \
    --name "$CONTAINER_NAME" \
    -p "${PORT}:8000" \
    "$IMAGE_NAME"

echo ""
echo "Готово. Приложение доступно по адресу: http://localhost:${PORT}"
echo "Логи: docker logs -f ${CONTAINER_NAME}"
