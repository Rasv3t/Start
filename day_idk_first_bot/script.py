import cv2
import numpy as np
import pyautogui
import time
import os
from PIL import ImageGrab
import logging
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class BattleCatsBot:
    def __init__(self):
        # Координаты для кликов (настройте под ваше окно BlueStacks)
        self.screen_width, self.screen_height = pyautogui.size()

        # Путь к папке с изображениями для распознавания
        self.templates_path = "templates"

        # Создаем папку для шаблонов, если её нет
        if not os.path.exists(self.templates_path):
            os.makedirs(self.templates_path)
            logging.info(f"Создана папка {self.templates_path}. Положите туда скриншоты кнопок.")

        # Координаты для призыва юнитов (нужно настроить под ваш экран)
        self.unit_positions = [
            (1600, 450),  # Юнит 1
            (1500, 450),  # Юнит 2
            (1300, 500),  # Юнит 3
            (1300, 450),
        ]

        # Время между призывами юнитов (в секундах)
        self.unit_spawn_delay = 0.01

        # Время ожидания после победы перед проверкой наград
        self.post_victory_delay = 5

        logging.info(f"Бот инициализирован. Размер экрана: {self.screen_width}x{self.screen_height}")

    def capture_screen(self):
        """Захват экрана"""
        screen = ImageGrab.grab()
        screen_np = np.array(screen)
        return cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

    def find_template(self, template_name, threshold=0.8):
        """Поиск шаблона на экране"""
        template_path = os.path.join(self.templates_path, template_name)
        if not os.path.exists(template_path):
            logging.warning(f"Шаблон {template_name} не найден")
            return None

        screen = self.capture_screen()
        template = cv2.imread(template_path)

        # Поиск шаблона
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y)

        return None

    def click(self, x, y, delay=0.3):
        """Клик в указанные координаты"""
        pyautogui.click(x, y)
        if delay > 0:
            time.sleep(delay)
        logging.info(f"Клик в координаты ({x}, {y})")

    def check_and_click_button(self, button_image, description, threshold=0.8, click_delay=0.3):
        """Проверка наличия кнопки и клик по ней"""
        position = self.find_template(button_image, threshold)
        if position:
            logging.info(f"Найдена кнопка: {description}")
            self.click(position[0], position[1], delay=click_delay)
            return True
        return False

    def wait_for_button(self, button_image, timeout=10, check_interval=0.5):
        """Ожидание появления кнопки на экране"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            position = self.find_template(button_image)
            if position:
                return position
            time.sleep(check_interval)
        return None

    def spawn_units(self, skip_first=False):
        """Призыв юнитов по сценарию"""
        logging.info("Начинаю призыв юнитов")

        # Если skip_first=True, используем только юнитов с индекса 1 (второй и третий)
        start_index = 1 if skip_first else 0

        # Цикл призыва юнитов
        for cycle in range(10):
            for i in range(start_index, len(self.unit_positions)):
                pos = self.unit_positions[i]
                logging.info(f"Призыв юнита {i + 1}, цикл {cycle + 1}")
                self.click(pos[0], pos[1], delay=0.3)

            time.sleep(self.unit_spawn_delay)

            # Проверка окончания уровня
            if self.check_level_complete():
                logging.info("Уровень завершен!")
                return True
        return False

    def handle_rewards(self):
        """Обработка окон с наградами после уровня"""
        logging.info("Обработка наград после уровня")

        # Координаты кнопки выхода (правый верхний угол)
        exit_x = 1850
        exit_y = 65

        # Список возможных окон с наградами
        reward_images = ['reward1.png', 'reward3.png']

        # Ждем появления любого окна с наградой (увеличил таймаут)
        reward_found = False
        for reward_img in reward_images:
            position = self.wait_for_button(reward_img, timeout=10)  # было 5, стало 10
            if position:
                logging.info(f"Найдено окно с наградой: {reward_img}")
                self.click(position[0], position[1], delay=2.0)  # было 1.0, стало 2.0
                reward_found = True
                break

        if not reward_found:
            logging.warning("Окно с наградой не найдено")
            return False

        # Дополнительная задержка перед кликом по выходу
        logging.info("Жду 2 секунды перед кликом по кнопке выхода...")
        time.sleep(2)  # Новая задержка

        # Клик по кнопке выхода по фиксированным координатам
        logging.info(f"Кликаю по кнопке выхода: ({exit_x}, {exit_y})")
        self.click(exit_x, exit_y, delay=3.0)  # было 2.0, стало 3.0

        return True

    def check_reward_popups(self):
        """Проверка всплывающих окон с наградами ВО ВРЕМЯ боя"""
        # Список возможных окон с наградами
        reward_images = ['reward1.png', 'reward3.png']

        for reward_img in reward_images:
            if self.check_and_click_button(reward_img, f"Окно награды {reward_img}", click_delay=0.5):
                time.sleep(0.5)
                return True
        return False

    def check_level_complete(self):
        """Проверка завершения уровня (поиск кнопки выхода)"""
        return self.find_template('exit_button.png') is not None

    def check_energy(self):
        """Проверка и восполнение энергии"""
        if self.check_and_click_button('no_energy.png', 'Нет энергии'):
            time.sleep(1)
            # Клик по кнопке использования флажка
            if self.check_and_click_button('flag_button.png', 'Кнопка с флажком'):
                time.sleep(1)
                # Подтверждение использования флажка
                self.check_and_click_button('confirm_flag.png', 'Подтверждение флажка')
                return True
        return False

    def run_farm_session(self, num_levels=10):
        """Запуск сессии фарма"""
        logging.info(f"Начинаю фарм сессию на {num_levels} уровней")

        levels_completed = 0

        while levels_completed < num_levels:
            try:
                # Ждем загрузки меню
                time.sleep(2)

                # Поиск и нажатие кнопки "Attack!"
                logging.info(f"Уровень {levels_completed + 1}: ищу кнопку Attack!")
                if not self.check_and_click_button('attack_button.png', 'Кнопка Attack!'):
                    logging.warning("Кнопка Attack! не найдена, жду...")
                    time.sleep(5)
                    continue

                # Ждем появления окна с энергией
                time.sleep(1.5)

                # Проверка окна с нехваткой энергии
                if self.handle_energy_popup():
                    logging.info("Флажок использован, ищу кнопку Attack! снова")
                    time.sleep(1)

                    if self.check_and_click_button('attack_button.png', 'Кнопка Attack! (после флажка)'):
                        logging.info("Attack! нажата, уровень начинается")
                        time.sleep(2)
                    else:
                        logging.error("Не удалось найти Attack! после использования флажка")
                        continue
                else:
                    logging.info("Окна с энергией нет, продолжаем")
                    time.sleep(2)

                # НОВАЯ ЛОГИКА: ждем 6 секунд, кликаем по первому юниту, потом спамим 2 и 3
                self.express_and_spawn_logic()

                # Ждем анимацию победы
                logging.info(f"Жду {self.post_victory_delay} секунд перед обработкой наград...")
                time.sleep(self.post_victory_delay)

                # Обработка наград после уровня
                if self.handle_rewards():
                    levels_completed += 1
                    logging.info(f"✓ Уровень {levels_completed} успешно завершен")
                else:
                    logging.error("✗ Не удалось обработать награды, пробую продолжить...")

                time.sleep(3)

            except Exception as e:
                logging.error(f"Ошибка во время фарма: {e}")
                time.sleep(5)

    def return_to_menu(self):
        """Возврат в главное меню (запасной вариант)"""
        logging.info("Возврат в меню")
        exit_x = self.screen_width - 50
        exit_y = 50
        self.click(exit_x, exit_y, delay=2)
        self.check_and_click_button('confirm_exit.png', 'Подтверждение выхода')

    def handle_energy_popup(self):
        """Обработка окна с нехваткой энергии - клик по флажку по координатам"""
        logging.info("Проверяю наличие окна с нехваткой энергии")

        # Ждем появления окна
        time.sleep(1.5)

        # Проверяем, появилось ли окно no_energy
        energy_position = self.find_template('no_energy.png', threshold=0.8)
        if energy_position:
            logging.info("Обнаружено окно 'Нет энергии', кликаю по флажку")

            # Клик по координатам флажка
            self.click(1300, 380, delay=1.5)
            return True

        return False

    def wait_for_express_and_click(self, timeout=30):
        """Ожидание появления экспресс-режима и клик по нему"""
        logging.info("Ожидаю появления экспресс-режима...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            position = self.find_template('express.png', threshold=0.8)
            if position:
                logging.info("Найден экспресс-режим, нажимаю!")
                self.click(position[0], position[1], delay=2)
                return True
            time.sleep(1)

        logging.warning("Экспресс-режим не найден, продолжаю без него...")
        return False

    def express_and_spawn_logic(self):
        """Экспресс-логика: четкая последовательность призыва юнитов"""
        logging.info("Запуск экспресс-логики")

        # Координаты юнитов
        pos1 = self.unit_positions[0]  # (1600, 450) - первый
        pos2 = self.unit_positions[1]  # (1500, 450) - второй
        pos3 = self.unit_positions[2]  # (1300, 500) - третий
        pos4 = self.unit_positions[3]  # Четвертый юнит (новый)

        # Ждем 5 секунд
        logging.info("Жду 5 секунд...")
        time.sleep(6)

        # Призываем юнита 1
        logging.info(f"Призываю юнита 1: ({pos1[0]}, {pos1[1]})")
        self.click(pos1[0], pos1[1], delay=0.3)

        # Ждем 4 секунды
        logging.info("Жду 4 секунды...")
        time.sleep(4)

        # Призываем юнита 2 (один раз)
        logging.info(f"Призываю юнита 2: ({pos2[0]}, {pos2[1]})")
        self.click(pos2[0], pos2[1], delay=0.3)

        # Призываем юнита 3 (один раз)
        logging.info(f"Призываю юнита 3: ({pos3[0]}, {pos3[1]})")
        self.click(pos3[0], pos3[1], delay=0.3)

        # Призываем юнита 4 (первый раз)
        logging.info(f"Призываю юнита 4 (1 раз): ({pos4[0]}, {pos4[1]})")
        self.click(pos4[0], pos4[1], delay=0.3)

        # Спамим юнитом 4 каждые 2.2 секунды, всего 3 раза (вместе с первым получится 4 раза)
        logging.info("Начинаю спам юнитом 4 каждые 2.2 секунды (еще 3 раза)...")
        for i in range(2):
            time.sleep(4.5)
            logging.info(f"Призываю юнита 4 (раз {i + 2}): ({pos4[0]}, {pos4[1]})")
            self.click(pos4[0], pos4[1], delay=0.3)

        logging.info("Экспресс-логика завершена")


def create_templates_guide():
    """Создание инструкции по созданию шаблонов"""
    guide = """
    Инструкция по созданию шаблонов для бота:

    1. Сделайте скриншоты следующих элементов в игре:
       - attack_button.png - кнопка "Attack!" в меню выбора уровня
       - no_energy.png - окно с сообщением о нехватке энергии
       - flag_button.png - кнопка использования флажка
       - confirm_flag.png - кнопка подтверждения использования флажка
       - reward1.png - окно с наградой (например, 1 билет)
       - reward3.png - окно с наградой (например, 3 билета)
       - exit_button.png - кнопка выхода из уровня (в правом верхнем углу)
       - confirm_exit.png - подтверждение выхода из уровня

    2. Сохраните все скриншоты в папку 'templates'
    3. Убедитесь, что скриншоты четкие и содержат только нужную кнопку

    Важно: Настройте координаты unit_positions под ваш экран!
    """
    print(guide)


if __name__ == "__main__":
    print("Battle Cats Bot")
    print("1. Запустить бота")
    print("2. Показать инструкцию по созданию шаблонов")

    choice = input("Выберите действие: ")

    if choice == "1":
        print("Бот запустится через 5 секунд. Переключитесь на окно BlueStacks!")
        time.sleep(5)

        bot = BattleCatsBot()

        # Дополнительная настройка времени ожидания
        custom_delay = input("Сколько секунд ждать после победы? (Enter - 3 сек): ")
        if custom_delay.strip():
            bot.post_victory_delay = int(custom_delay)

        # Запуск фарма
        levels = int(input("Сколько уровней хотите пройти? "))
        bot.run_farm_session(levels)

    elif choice == "2":
        create_templates_guide()
    else:
        print("Wrong select")