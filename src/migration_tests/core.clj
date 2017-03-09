(ns migration-tests.core
  (:require [clojure.java.jdbc :as jdbc])
  (:gen-class))

(def db-spec
  {:classname "com.mysql.jdbc.Driver"
   :subprotocol "mysql"
   :subname "//james:3306/nova"
   :user "root"
   :password "56592b2f97c7de918edd"})

(defn exec-sql-file [file-name]
  (jdbc/query db-spec ["SELECT * FROM instances"]))

(defn -main
  [& args]
  (let [case "add_index"]
    (exec-sql-file (str "cases/" case "init.sql"))
    (println "Hello, World!")))
