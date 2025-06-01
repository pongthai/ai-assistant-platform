# controller package initializer
import logging

logging.basicConfig(
    level=logging.INFO,  # หรือ DEBUG เพื่อให้เห็นทั้งหมด
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)