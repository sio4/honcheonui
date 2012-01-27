class User < ActiveRecord::Base
  # Include default devise modules. Others available are:
  # :token_authenticatable, :encryptable, :confirmable, :lockable, :timeoutable and :omniauthable
  devise :ldap_authenticatable, :registerable,
         :token_authenticatable,
         :recoverable, :rememberable, :trackable, :validatable

  # Setup accessible (or protected) attributes for your model
  attr_accessible :email, :password, :password_confirmation, :remember_me
  attr_accessible :admin, :active, :level, :name, :mail, :mobile, :uid, :theme
  attr_accessible :sign_in_count, :last_sign_in_at, :last_sign_in_ip

  before_save :ldap_information
  before_save :ensure_authentication_token!

  def ldap_information
    Rails::logger.info("import LDAP_INFORMATION (but site specific!!!)")
    begin
      temp = Devise::LdapAdapter.get_ldap_param(self.email, 'name')
      self.name = temp.gsub(/\(.*\)/, '')
      temp = Devise::LdapAdapter.get_ldap_param(self.email, 'mail')
      self.mail = temp
      temp = Devise::LdapAdapter.get_ldap_param(self.email, 'mobile')
      self.mobile = temp
      temp = Devise::LdapAdapter.get_ldap_param(self.email, 'department')
      self.department = temp
    rescue NoMethodError
      # ignore
    end
  end
end
