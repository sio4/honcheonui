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

ActiveRecord::Schema.define(:version => 20120120084215) do

  create_table "logs", :force => true do |t|
    t.datetime "logdate"
    t.integer  "server_id"
    t.string   "process"
    t.integer  "pid"
    t.string   "message"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.string   "group"
  end

  add_index "logs", ["server_id"], :name => "index_logs_on_server_id"

  create_table "servers", :force => true do |t|
    t.string   "name"
    t.text     "desc"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.string   "uuid"
    t.boolean  "confirmed",     :default => false
    t.string   "os_name"
    t.string   "os_rel"
    t.string   "os_id"
    t.string   "os_kernel"
    t.string   "os_build"
    t.string   "os_arch"
    t.string   "op_mode"
    t.string   "op_level"
    t.integer  "st_uptime"
    t.boolean  "st_monitoring", :default => false
    t.boolean  "st_automation", :default => false
  end

  create_table "stats", :force => true do |t|
    t.integer  "server_id"
    t.datetime "dt"
    t.integer  "cpu_user_max"
    t.integer  "cpu_user_avg"
    t.integer  "cpu_sys_max"
    t.integer  "cpu_sys_avg"
    t.integer  "cpu_wait_max"
    t.integer  "cpu_wait_avg"
    t.integer  "mem_used"
    t.integer  "mem_buffer"
    t.integer  "mem_cached"
    t.integer  "swp_used"
    t.integer  "task_total"
    t.integer  "task_running"
    t.integer  "task_blocked"
    t.integer  "task_zombie"
    t.integer  "users"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "stats", ["server_id"], :name => "index_stats_on_server_id"

  create_table "taglinks", :force => true do |t|
    t.string   "name"
    t.text     "description"
    t.integer  "star_id"
    t.string   "star_type"
    t.integer  "tag_id"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "taglinks", ["star_id"], :name => "index_taglinks_on_star_id"
  add_index "taglinks", ["tag_id"], :name => "index_taglinks_on_tag_id"

  create_table "tags", :force => true do |t|
    t.string   "name",                           :null => false
    t.text     "description"
    t.string   "category",    :default => "tag"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  create_table "users", :force => true do |t|
    t.string   "email",                                 :default => "",      :null => false
    t.string   "encrypted_password",     :limit => 128, :default => "",      :null => false
    t.string   "reset_password_token"
    t.datetime "reset_password_sent_at"
    t.datetime "remember_created_at"
    t.integer  "sign_in_count",                         :default => 0
    t.datetime "current_sign_in_at"
    t.datetime "last_sign_in_at"
    t.string   "current_sign_in_ip"
    t.string   "last_sign_in_ip"
    t.integer  "failed_attempts",                       :default => 0
    t.string   "unlock_token"
    t.datetime "locked_at"
    t.string   "authentication_token"
    t.string   "uid"
    t.boolean  "admin",                                 :default => false
    t.boolean  "active",                                :default => false
    t.integer  "level",                                 :default => 1
    t.string   "name"
    t.string   "mail"
    t.string   "mobile"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.string   "theme",                                 :default => "black"
  end

  add_index "users", ["authentication_token"], :name => "index_users_on_authentication_token", :unique => true
  add_index "users", ["email"], :name => "index_users_on_email", :unique => true
  add_index "users", ["reset_password_token"], :name => "index_users_on_reset_password_token", :unique => true
  add_index "users", ["unlock_token"], :name => "index_users_on_unlock_token", :unique => true

end
