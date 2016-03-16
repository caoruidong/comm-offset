#include <linux/module.h>
#include <linux/sched.h>

int init_module()
{
	printk(KERN_INFO "offset in task_struct is 0x%lx\n", offsetof(struct task_struct, comm));
	return 0;
}

void cleanup_module() { }
