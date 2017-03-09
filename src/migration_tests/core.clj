(ns migration-tests.core
  (:require [clojure.java.jdbc :as jdbc]
            [clojure.string :as str])
  (:gen-class))

(def db-spec
  {:classname "com.mysql.jdbc.Driver"
   :subprotocol "mysql"
   :subname "//james:3306/nova"
   :user "root"
   :password "56592b2f97c7de918edd"})

(defn skip-line? [line]
  (let [line (str/trim line)]
   (or (empty? line) (str/starts-with? line "--"))))

(defn split-sql-statements [text]
  "Naive way of splitting sql statements.
   Strings with semicolons and multi-line comments are not supported"
  (remove skip-line? (str/split text #";" )))

(defn exec-sql-file [file-name]
  (jdbc/db-do-commands db-spec (split-sql-statements (slurp file-name))))

(defn -main
  [& args]
  (let [case "add_index"]
    (exec-sql-file (str "cases/" case "/init.sql"))
    (println "Done!")))
