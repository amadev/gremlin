(ns migration-tests.core
  (:require [clojure.java.jdbc :as jdbc]
            [clojure.string :as str]
            [clojure.tools.logging :as log])
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

(defn case-name [case name]
  (str "cases/" case "/" name ".sql"))

(defn -main
  [& args]
  (let [cs "add_index"]
    (log/debug "Starting ...")
    (exec-sql-file (case-name cs "init"))
    (println "Done!")))
