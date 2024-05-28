from genie.testbed import load
from pyats.topology import loader
from pyats import aetest
import re, logging
import pdb
from pyats.results import Passed,Failed
from pyats.async_.exceptions import *
from acl_lib import acl_common_functions
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
import time
global device_list

#easypy job_file -t testbed_yaml_file -datafile datafile

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def print_testbed_information(self,testbed):
        pdb.set_trace()
        global uut1,uut2,uut3,device_list,device_info
        uut1 = testbed.devices['dut1']
        self.parent.parameters.update(uut1 = uut1)
        uut2 = testbed.devices['dut3']
        self.parent.parameters.update(uut2 = uut2)
        uut3 = testbed.devices['dut2']
        self.parent.parameters.update(uut3 = uut3)

        device_list = [uut1,uut2,uut3]
        device_info = {}

        if not testbed:
            logging.info("No testbed was provided to script launch")
        else:
            uut = testbed.devices['dut1']
            for device in testbed:
                logging.info("Device name : %s "%device.name)
                device_info.update({device.name: []})
                for intf in device:
                   logging.info("Interface : %s"%intf.name)
                   device_info[device.name].append(intf.name)
                   if intf.link:
                       logging.info("Link : %s"%intf.link.name)
                   else:
                       logging.info("Link : None")
            logger.info("Device and interfaces used for acl feature")
            logger.info(device_info)

    @aetest.subsection
    def connect_to_devices(self,testbed):
        logger.info("Connecting to devices")
        for uut in device_list:
            uut.connect()
            if uut.is_connected() == True:
                logging.info("Successfully connected to device %s"%uut.name)
                output = uut.execute('show version')
                res = acl_common_functions.sh_version(output)
                logging.info("Software version :%s"%res['version'])
                logging.info("Image File :%s"%res['image'])
            else:
                logging.info("Device %s not connected"%uut.name)

    @aetest.subsection
    def configure_ip_address_to_interfaces(self,testbed):
        logger.info("Assign ip address to interfaces")
        pdb.set_trace()
        logger.info(device_info.keys())
        #for dev in device_info.keys():
        acl_common_functions.configure_ip_address(uut1,device1['intf'],device1['ip_address'],subnet_mask)
        acl_common_functions.configure_ip_address(uut2,device2['intf1'],device2['ip_address1'],subnet_mask)
        acl_common_functions.configure_ip_address(uut2,device2['intf2'],device2['ip_address2'],subnet_mask)
        acl_common_functions.configure_ip_address(uut3,device3['intf'],device3['ip_address'],subnet_mask)

    @aetest.subsection
    def enable_rip_on_device(self,testbed):
        logging.info("Enable rip on devices")
        for uut in device_list:
            acl_common_functions.enable_rip(uut)

    @aetest.subsection
    def configure_rip_on_devices(self,testbed):
        logger.info("Configure rip on interfaces")
        acl_common_functions.configure_rip(uut1,device1['intf'])
        acl_common_functions.configure_rip(uut2,device2['intf1'])
        acl_common_functions.configure_rip(uut2,device2['intf2'])
        acl_common_functions.configure_rip(uut3,device3['intf'])

#@aetest.skip("testing fourth scenario")
class acl_testcase_permit(aetest.Testcase):

    @aetest.setup
    def configure_acl_on_device(self,testbed):

        logger.info("Configure acl on device3:{}".format(uut2.name))
        acl_common_functions.configure_acl(uut2,acl_name,rule1)

        logger.info("Configure acl in interface")
        acl_common_functions.configure_acl_interface(uut2,device2['intf1'],acl_name,bound)

    @aetest.test
    def check_ping_after_permit_acl(self,testbed):
        logger.info("Check acl configured or not ")
        acl_config = uut2.execute("show access-list {}".format(acl_name))
        logger.info(acl_config)
        if acl_name in acl_config:
            logger.info("ACL configured on device")
        else:
            self.errored('Acl is not configured on device')

        logger.info("Ping the ip configured on device2: {}".format(uut3.name))
        for i in range(5):
            result = uut2.execute("ping {}".format(device3['ip_address']))
            time.sleep(10)
        res_dict = acl_common_functions.validate_ping(result)
        time.sleep(10)
        logger.info("++++++++++++++++++++++++++++")
        logger.info(res_dict)
        logger.info("++++++++++++++++++++++++++++")

        if ((res_dict['sent_pkt'] == res_dict['receive_pkt']) and (res_dict['pkt_loss'] == '0.00%')):
            logger.info("Sent : {} packets and received: {} packets and packet loss: {}".format(res_dict['sent_pkt'],res_dict['receive_pkt'],res_dict['pkt_loss']))
            self.passed("Success: After applied permit rule for acl, ping got successful")
        else:
            logger.info("Sent : {} packets and received: {} packets and packet loss: {}".format(res_dict['sent_pkt'],res_dict['receive_pkt']
,res_dict['pkt_loss']))
            self.failed("Failed: After applied permit rule for acl, ping got failed")


    @aetest.cleanup
    def unconfigure_acl_on_device(self,testbed):
        logger.info("Unconfigure acl in interface")
        acl_common_functions.unconfigure_acl_interface(uut2,device2['intf2'],acl_name,bound)

        logger.info("Unconfigure acl on device3:{}".format(uut2.name))
        acl_common_functions.unconfigure_acl(uut2,acl_name)

#@aetest.skip("testing fourth scenario")
class acl_testcase_deny(aetest.Testcase):

    @aetest.setup
    def configure_acl_on_device(self,testbed):

        logger.info("Configure acl on device1:{}".format(uut1.name))
        acl_common_functions.configure_acl(uut1,acl_name,rule2)

        logger.info("Configure acl in interface")
        acl_common_functions.configure_acl_interface(uut1,device1['intf'],acl_name,bound)

    @aetest.test
    def check_ping_after_deny_acl(self,testbed):

        logger.info("Check acl configured or not ")
        acl_config = uut1.execute("show access-list {}".format(acl_name))
        logger.info(acl_config)
        if acl_name in acl_config:
            logger.info("ACL configured on device")
        else:
            self.errored('Acl is not configured on device')

        logger.info("Ping the ip configured on device2: {}".format(uut3.name))
        for i in range(3):
            result = uut1.execute("ping {}".format(device3['ip_address']))
        res_dict = acl_common_functions.validate_ping(result)
        logger.info("++++++++++++++++++++++++++++")
        logger.info(res_dict)
        logger.info("++++++++++++++++++++++++++++")

        if ((res_dict['sent_pkt'] != res_dict['receive_pkt']) and (res_dict['pkt_loss'] == '100.00%')):
            logger.info("Sent : {} packets and received: {} packets and packet loss: {}".format(res_dict['sent_pkt'],res_dict['receive_pkt'],res_dict['pkt_loss']))
            self.passed("Success: After applied deny rule for acl ping got failed")
        else:
            logger.info("Sent : {} packets and received: {} packets and packet loss: {}".format(res_dict['sent_pkt'],res_dict['receive_pkt']
,res_dict['pkt_loss']))
            self.failed("Failed: After applied deny rule for acl ping got successful")

    @aetest.cleanup
    def unconfigure_acl_on_device(self,testbed):
        logger.info("Unconfigure acl in interface")
        acl_common_functions.unconfigure_acl_interface(uut1,device1['intf'],acl_name,bound)

        logger.info("Unconfigure acl on device3:{}".format(uut1.name))
        acl_common_functions.unconfigure_acl(uut1,acl_name)

#@aetest.skip("testing fourth scenario")
class acl_testcase_multiple_rules(aetest.Testcase):

    @aetest.setup
    def configure_acl_on_device(self,testbed):

        logger.info("Configure acl on device1:{}".format(uut1.name))
        acl_common_functions.configure_acl(uut1,acl_name,rule3)

        logger.info("Configure acl on device1:{}".format(uut1.name))
        acl_common_functions.configure_acl(uut1,acl_name,rule2)

        logger.info("Configure acl in interface")
        acl_common_functions.configure_acl_interface(uut1,device1['intf'],acl_name,bound)

    @aetest.test
    def check_ping_after_multiple_acl_rules(self,testbed):

        logger.info("Check acl configured or not ")
        acl_config = uut1.execute("show access-list {}".format(acl_name))
        logger.info(acl_config)
        if acl_name in acl_config:
            logger.info("ACL configured on device")
        else:
            self.errored('Acl is not configured on device')

        logger.info("Ping the ip configured on device3 and device1: {} {}".format(uut1.name,uut3.name))
        for i in range(1):
            result2 = uut1.execute("ping {}".format(device3['ip_address']))
        res_dict2 = acl_common_functions.validate_ping(result2)
        logger.info("++++++++++++++++++++++++++++")
        logger.info(res_dict2)
        logger.info("++++++++++++++++++++++++++++")

        for i in range(3):
            result1 = uut2.execute("ping {}".format(device1['ip_address']))
        res_dict1 = acl_common_functions.validate_ping(result1)
        logger.info("++++++++++++++++++++++++++++")
        logger.info(res_dict1)
        logger.info("++++++++++++++++++++++++++++")


        if (res_dict1['sent_pkt'] == res_dict1['receive_pkt']) and (res_dict1['pkt_loss'] == '0.00%'):
            res1 = True
        else:
            res1 = False

        if (res_dict2['sent_pkt'] != res_dict2['receive_pkt']) and (res_dict2['pkt_loss'] == '100.00%'):
            res2 = True
        else:
            res2 = False

        if (res1 and res2):
            self.passed("Success: After applied deny and permit rule for acl ping got failed for deny rule and got successful for permit rule")
        else:
            self.failed("Failed: Multiple acl rule are not working")


    @aetest.cleanup
    def unconfigure_acl_on_device(self,testbed):
        logger.info("Unconfigure acl in interface")
        acl_common_functions.unconfigure_acl_interface(uut1,device1['intf'],acl_name,bound)

        logger.info("Unconfigure acl on device3:{}".format(uut1.name))
        acl_common_functions.unconfigure_acl(uut1,acl_name)

#@aetest.skip('testing another testcase')
class acl_testcase_in_out_bound(aetest.Testcase):

    @aetest.setup
    def configure_acl_on_device(self,testbed):

        logger.info("Configure acl on device3:{}".format(uut2.name))
        acl_common_functions.configure_acl(uut2,acl_name,rule1)

        logger.info("Configure acl in interface")
        acl_common_functions.configure_acl_interface(uut2,device2['intf1'],acl_name,bound)

    @aetest.test
    def check_ping_after_in_out_bound_acl(self,testbed):

        logger.info("Check acl configured or not ")
        acl_config = uut2.execute("show access-list {}".format(acl_name))
        logger.info(acl_config)
        if acl_name in acl_config:
            logger.info("ACL configured on device")
        else:
            self.errored('Acl is not configured on device')

        logger.info("Ping the ip configured on device2: {} to check in bound".format(uut3.name))
        for i in range(3):
            result1 = uut2.execute("ping {}".format(device3['ip_address']))
        res_dict1 = acl_common_functions.validate_ping(result1)
        logger.info("++++++++++++++++++++++++++++")
        logger.info(res_dict1)
        logger.info("++++++++++++++++++++++++++++")

        if (res_dict1['sent_pkt'] == res_dict1['receive_pkt']) and (res_dict1['pkt_loss'] == '0.00%'):
            res1 = True
        else:
            res1 = False


        logger.info("Unconfigure in bound acl in interface")
        acl_common_functions.unconfigure_acl_interface(uut2,device2['intf2'],acl_name,bound)

        logger.info("Configure out bound acl in interface")
        acl_common_functions.configure_acl_interface(uut2,device2['intf2'],acl_name,bound1)

        logger.info("Ping the ip configured on device2: {}".format(uut3.name))
        for i in range(3):
            result2 = uut2.execute("ping {}".format(device2['ip_address1']))
        res_dict2 = acl_common_functions.validate_ping(result2)
        logger.info("++++++++++++++++++++++++++++")
        logger.info(res_dict2)
        logger.info("++++++++++++++++++++++++++++")

        if (res_dict2['sent_pkt'] == res_dict2['receive_pkt']) and (res_dict2['pkt_loss'] == '0.00%'):
            res2 = True
        else:
            res2 = False

        if res1 and res2:
            self.passed("Success: in and out bound working successfully")
        else:
            self.failed("Failed: in and out bound not working")


    @aetest.cleanup
    def unconfigure_acl_on_device(self,testbed):
        logger.info("Unconfigure acl in interface")
        acl_common_functions.unconfigure_acl_interface(uut2,device2['intf2'],acl_name,bound1)

        logger.info("Unconfigure acl on device3:{}".format(uut2.name))
        acl_common_functions.unconfigure_acl(uut2,acl_name)

#@aetest.skip("testing fourth scenario")
class acl_testcase_configured(aetest.Testcase):

    @aetest.setup
    def configure_acl_on_device(self,testbed):

        logger.info("Configure acl on device1:{}".format(uut1.name))
        acl_common_functions.configure_acl(uut1,acl_name,rule2)

    @aetest.test
    def check_acl_configured(self,testbed):
        logger.info("Check acl configured or not ")
        result = uut1.execute("show access-list {}".format(acl_name))
        logger.info(result)

        if result:
            logger.info("acl configured")
            self.passed("Success: acl is configured on device and on interface successfully")
        else:
            logger.info("acl not configured")
            self.failed("Failed: acl is not configured on device and on interface")

    @aetest.cleanup
    def unconfigure_acl_on_device(self,testbed):
        logger.info("Unconfigure acl on device3:{}".format(uut1.name))
        acl_common_functions.unconfigure_acl(uut1,acl_name)

#@aetest.skip("testing fourth scenario")
class acl_testcase_not_configured(aetest.Testcase):

    @aetest.test
    def check_acl__not_configured(self,testbed):
        logger.info("Check acl not configured on device")
        result = uut1.execute("show access-list")
        logger.info(result)

        if acl_name not in result:
            logger.info("acl named {} not configured on device".format(acl_name))
            self.passed("Success: acl {} not configured on device and on interface successfully".format(acl_name))
        else:
            logger.info("acl configured")
            self.failed("Failed: acl is configured on device and on interface")

#@aetest.skip("testing fourth scenario")
class acl_testcase_check_acl_configured_on_interface(aetest.Testcase):

    @aetest.setup
    def configure_acl_on_device(self,testbed):

        logger.info("Configure acl on device1:{}".format(uut1.name))
        acl_common_functions.configure_acl(uut1,acl_name,rule2)

        logger.info("Configure acl in interface")
        acl_common_functions.configure_acl_interface(uut1,device1['intf'],acl_name,bound)

    @aetest.test
    def check_acl_not_configured_on_interface(self,testbed):
        logger.info("Check acl configured on interface")
        result1 = uut1.execute("show running-config interface {}".format(device1['intf']))
        logger.info(result1)

        if acl_name in result1:
            logger.info("acl named {} not configured on interface {}".format(acl_name,device1['intf']))
            self.passed("Success: acl {} not configured on interface {} of device {}".format(acl_name,device1['intf'],uut1.name))
        else:
            logger.info("acl not configured on interface")
            self.failed("Failed : acl {} configured on interface {} of device {}".format(acl_name,device1['intf'],uut1.name))

    @aetest.cleanup
    def unconfigure_acl_on_device(self,testbed):

        logger.info("Unconfigure acl in interface")
        acl_common_functions.unconfigure_acl_interface(uut1,device1['intf'],acl_name,bound)

        logger.info("Unconfigure acl on device3:{}".format(uut1.name))
        acl_common_functions.unconfigure_acl(uut1,acl_name)

#@aetest.skip("testing fourth scenario")
class acl_testcase_check_acl_not_configured_on_interface(aetest.Testcase):

    @aetest.setup
    def configure_acl_on_device(self,testbed):

        logger.info("Configure acl on device1:{}".format(uut1.name))
        acl_common_functions.configure_acl(uut1,acl_name,rule2)

    @aetest.test
    def check_acl_not_configured_on_interface(self,testbed):
        logger.info("Check acl not configured on interface")
        result1 = uut1.execute("show running-config interface {}".format(device1['intf']))
        logger.info(result1)

        if acl_name not in result1:
            logger.info("acl named {} not configured on interface {}".format(acl_name,device1['intf']))
            self.passed("Success: acl {} not configured on interface {} of device {}".format(acl_name,device1['intf'],uut1.name))
        else:
            logger.info("acl not configured on interface")
            self.failed("Failed : acl {} configured on interface {} of device {}".format(acl_name,device1['intf'],uut1.name))

    @aetest.cleanup
    def unconfigure_acl_on_device(self,testbed):

        logger.info("Unconfigure acl on device3:{}".format(uut1.name))
        acl_common_functions.unconfigure_acl(uut1,acl_name)

class CommonCleanup(aetest.CommonCleanup):

    @aetest.subsection
    def unconfigure_rip_on_devices(self,testbed):
        logger.info("Unconfigure rip on interfaces")
        acl_common_functions.unconfigure_rip(uut1,device1['intf'])
        acl_common_functions.unconfigure_rip(uut2,device2['intf1'])
        acl_common_functions.unconfigure_rip(uut2,device2['intf2'])
        acl_common_functions.unconfigure_rip(uut3,device3['intf'])

    @aetest.subsection
    def disable_rip_on_device(self,testbed):
        logging.info("disable rip on devices")
        for uut in device_list:
            acl_common_functions.disable_rip(uut)

    @aetest.subsection
    def unconfigure_ipaddress_device(self,testbed):
        logging.info("Unconfig ip address on interfaces of all devices")
        acl_common_functions.unconfigure_ip_address(uut1,device1['intf'])
        acl_common_functions.unconfigure_ip_address(uut2,device2['intf1'])
        acl_common_functions.unconfigure_ip_address(uut2,device2['intf2'])
        acl_common_functions.unconfigure_ip_address(uut3,device3['intf'])

    @aetest.subsection
    def disconnect(self,testbed):
        logger.info("Disconnect the devices")
        for uut in device_list:
            uut.disconnect()


if __name__ == '__main__':
    import argparse
    from pyats.topology import loader

    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest = 'testbed',
                        type = loader.load)

    args, unknown = parser.parse_known_args()

    aetest.main(**vars(args))
