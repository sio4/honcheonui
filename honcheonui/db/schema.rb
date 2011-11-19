# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your
# database schema. If you need to create the application database on another
# system, you should be using db:schema:load, not running all the migrations
# from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended to check this file into your version control system.

ActiveRecord::Schema.define(:version => 20111119030017) do

  create_table "logs", :force => true do |t|
    t.datetime "logdate"
    t.integer  "server_id"
    t.string   "process"
    t.integer  "pid"
    t.string   "message"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "logs", ["server_id"], :name => "index_logs_on_server_id"

  create_table "servers", :force => true do |t|
    t.string   "name"
    t.string   "status"
    t.text     "desc"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

end
