-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema wish_app
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `wish_app` ;

-- -----------------------------------------------------
-- Schema wish_app
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `wish_app` DEFAULT CHARACTER SET utf8 ;
USE `wish_app` ;

-- -----------------------------------------------------
-- Table `wish_app`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `wish_app`.`users` ;

CREATE TABLE IF NOT EXISTS `wish_app`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(255) NULL,
  `last_name` VARCHAR(255) NULL,
  `email` VARCHAR(255) NULL,
  `password` VARCHAR(255) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `wish_app`.`wishes`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `wish_app`.`wishes` ;

CREATE TABLE IF NOT EXISTS `wish_app`.`wishes` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `wish_content` VARCHAR(255) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_wishes_users_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_wishes_users`
    FOREIGN KEY (`user_id`)
    REFERENCES `wish_app`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `wish_app`.`likes`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `wish_app`.`likes` ;

CREATE TABLE IF NOT EXISTS `wish_app`.`likes` (
  `user_id` INT NOT NULL,
  `wish_id` INT NOT NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  INDEX `fk_users_has_wishes_wishes1_idx` (`wish_id` ASC) VISIBLE,
  INDEX `fk_users_has_wishes_users1_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_users_has_wishes_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `wish_app`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_users_has_wishes_wishes1`
    FOREIGN KEY (`wish_id`)
    REFERENCES `wish_app`.`wishes` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
