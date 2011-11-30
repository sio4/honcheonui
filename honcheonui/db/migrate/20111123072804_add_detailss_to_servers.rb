class AddDetailssToServers < ActiveRecord::Migration
  def up
    add_column :servers, :uuid, :string
    add_column :servers, :confirmed, :boolean, :default => false
    add_column :servers, :os_name, :string
    add_column :servers, :os_rel, :string
    add_column :servers, :os_id, :string
    add_column :servers, :os_kernel, :string
    add_column :servers, :os_build, :string
    add_column :servers, :os_arch, :string
    add_column :servers, :op_mode, :string
    add_column :servers, :op_level, :string
    add_column :servers, :st_uptime, :integer
    add_column :servers, :st_monitoring, :boolean, :default => false
    add_column :servers, :st_automation, :boolean, :default => false
    remove_column :servers, :status
  end

  def down
    remove_column :servers, :uuid
    remove_column :servers, :confirmed
    remove_column :servers, :os_name
    remove_column :servers, :os_rel
    remove_column :servers, :os_id
    remove_column :servers, :os_kernel
    remove_column :servers, :os_build
    remove_column :servers, :os_arch
    remove_column :servers, :op_mode
    remove_column :servers, :op_level
    remove_column :servers, :st_uptime
    remove_column :servers, :st_monitoring
    remove_column :servers, :st_automation
    add_column :servers, :status, :string
  end
end
