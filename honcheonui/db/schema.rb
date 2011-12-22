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

ActiveRecord::Schema.define(:version => 20111207075826) do

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

end
