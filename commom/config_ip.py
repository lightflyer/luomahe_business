# -*- coding:utf-8 -*-

import wmi

obj_nic_config = None
arr_ip_addresses = ['192.168.70.120', '192.168.1.56']  # IP地址列表
arr_subnet_masks = ['255.255.255.0', '255.255.255.0']  # 子网掩码列表
arr_default_gateways = ['192.168.70.253']  # 默认网关列表
arr_gateway_cost_metrics = [1]  # 默认网关跳跃点
arr_dns_servers = {'mobile': ['202.101.98.55'],
                   'telecommunication': ['218.85.157.99', '202.101.115.55']
                   }  # 福建DNS服务器列表，详见 http://114.xixik.com/chinadns/
int_reboot = 0


def get_nic_config():
    wmi_service = wmi.WMI()
    col_nic_configs = wmi_service.Win32_NetworkAdapterConfiguration(IPEnabled=True)
    # 根据需要过滤出指定网卡，本只有一个网卡，不做过滤直接获取第一个
    '''
    for obj in col_nic_configs:
        print(obj.Index)
        print(obj.Description)
        print(obj.SettingID)
    '''
    if len(col_nic_configs) < 1:
        print('没有找到可用的网络适配器')
        return False
    else:
        global obj_nic_config
        obj_nic_config = col_nic_configs[0]
        return True


def set_ip():

    return_value = obj_nic_config.EnableStatic(IPAddress=arr_ip_addresses, SubnetMask=arr_subnet_masks)
    if return_value[0] == 0:
        print('设置IP成功')
    elif return_value[0] == 1:
        print('设置IP成功')
        global int_reboot
        int_reboot += 1
    else:
        print('ERROR: IP设置发生错误')
        return False
    return True


def set_gateways():
    return_value = obj_nic_config.SetGateways(DefaultIPGateway=arr_default_gateways, GatewayCostMetric=arr_gateway_cost_metrics)
    if return_value[0] == 0:
        print('设置网关成功')
    elif return_value[0] == 1:
        print('设置网关成功')
        global int_reboot
        int_reboot += 1
    else:
        print('ERROR: 网关设置发生错误')
        return False
    return True


def set_dns():
    return_value = obj_nic_config.SetDNSServerSearchOrder(DNSServerSearchOrder=arr_dns_servers['mobile'])
    if return_value[0] == 0:
        print('设置DNS成功')
    elif return_value[0] == 1:
        print('设置DNS成功')
        global int_reboot
        int_reboot += 1
    else:
        print('ERROR: DNS设置发生错误')
        return False
    return True


def set_auto_dns():
    return_value = obj_nic_config.SetDNSServerSearchOrder()
    if return_value[0] == 0:
        print('设置自动获取DNS成功')
    elif return_value[0] == 1:
        print('设置自动获取DNS成功')
        global int_reboot
        int_reboot += 1
    else:
        print('ERROR: DNS设置发生错误')
        return False
    return True


def SetAutoIP():
    return_value = obj_nic_config.EnableDHCP()
    if return_value[0] == 0:
        print('设置自动获取IP成功')
    elif return_value[0] == 1:
        print('设置自动获取IP成功')
        global int_reboot
        int_reboot += 1
    else:
        print('ERROR: IP设置发生错误')
        return False
    return True


# 切换为静态IP
def EnableStatic():
    return set_ip() and set_gateways() and set_dns()


# 切换为自动获取IP、DNS
def EnableDHCP():
    return set_auto_dns() and SetAutoIP()


def main():
    if not get_nic_config():
        return False

    if obj_nic_config.DHCPEnabled:
        print('正在切换为静态IP...')
        if EnableStatic():
            if int_reboot > 0:
                print('需要重新启动计算机')
            else:
                print('修改后的配置为：')
                print('IP: ', ', '.join(obj_nic_config.IPAddress))
                print('掩码: ', ', '.join(obj_nic_config.IPSubnet))
                print('网关: ', ', '.join(obj_nic_config.DefaultIPGateway))
                print('DNS: ', ', '.join(obj_nic_config.DNSServerSearchOrder))
                print('修改IP结束')
        else:
            print('请关闭控制面板、以管理员权限运行重试')
    else:
        print('正在切换为动态IP...')
        if EnableDHCP():
            if int_reboot > 0:
                print('需要重新启动计算机')
            else:
                print('切换为动态DHCP成功!')
        else:
            print('请关闭控制面板、以管理员权限运行重试')


if __name__ == "__main__":
    main()