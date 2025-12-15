#!/bin/bash
# fuser -k 8011/tcp
# source ./backend/venv/bin/activate
# python3 backend/manage.py runserver 0.0.0.0:8011

# === Цвета ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# === Меню: команды по популярности ===
show_menu() {
    clear
    echo -e "${GREEN} === FASTAPI === ${NC}"
    echo " 1) запустить сервер FASTAPI в режиме reload"    
    echo " 3) запустить Arq Worker"
    echo " 4) запустить Longpool Объявления"
    echo " 5) source venv/bin/activate"
    echo " 6) deactivate"
    echo " 7) Создать миграцию Alembic"
    echo " 8) Применить миграцию Alembic" 
    echo -e " 9) ${BLUE}→ Обновления записей ${NC}"
    echo " 10) запустить Celery worker"
    echo
    echo "0) Выход"
    echo -n "Выберите команду [0-16]: "
}

# === Основной цикл ===
while true; do
    show_menu
    read -r choice
    case $choice in
        1)
            echo -e "${BLUE} FASTAPI SERVER RUN ${NC}"
            # alembic upgrade head
            uvicorn app.main:app --no-access-log --reload --port 8123
            read -rp "Нажмите для продолжения ..." 
            ;;        
        3)
            # celery -A celery_app worker --loglevel=info --queues=longpoll   
            arq app.vk.arq.worker.WorkerSettings     
            read -rp "Нажмите для продолжения ..."   
            ;;
        4)
            python app/vk/longpoll/obyavlenie.py   
            read -rp "Нажмите для продолжения ..."         
            ;;
            
        5)
            source venv/bin/activate            
            ;;
        6)
            deactivate
            ;;
        7)
            # После этого alembic revision --autogenerate будет видеть все модели.
            echo -e "${BLUE}→ Создание миграции Alembic ${NC}"
            read -rp "Введите комментарий " comment 
            alembic revision --autogenerate -m "$comment"
            # alembic revision --autogenerate -m "rename post_id to vk_id in vk_obyavlenie_post"
            # alembic revision --autogenerate -m "fix"   
            read -rp "Нажмите для продолжения ..."
            ;;
        8)
            # После этого alembic revision --autogenerate будет видеть все модели.
            echo -e "${BLUE}→ Применение миграции Alembic ${NC}" 
            alembic upgrade head
            read -rp "Нажмите для продолжения ..."
            ;;
        9)
            # После этого alembic revision --autogenerate будет видеть все модели.
            echo -e "${BLUE}→ CLI: Обновления записей ${NC}" 
            python cli/posts.py view
            read -rp "Введите ID группы для обновления записей " id_group 
            
            python cli/posts.py run "$id_group"
            read -rp "Нажмите для продолжения ..."
            ;;
        10)
            # celery -A celery_app worker --loglevel=info --queues=longpoll   
            celery -A celery_app worker --loglevel=info     
            read -rp "Нажмите для продолжения ..."   
            ;;

            
        0)            
            break
            ;;
        *)
            echo -e "${RED}❌ Неверный выбор. Попробуйте снова.${NC}"
            ;;
    esac
    echo ""
done