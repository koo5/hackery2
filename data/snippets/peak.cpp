

bool TuningWidget::checkPeaks()
{	
	QString msgs;
	bool left_found = false;
	bool right_found  = false;
	int max = 0;
	int right_min = limits::max<int>();
	int left_min = limits::max<int>();
	for (vc: graph) {
		y = vc.y;
		if (left_min < y)
			left_min = y
		if (y - left_min > noise)
			left_found = true;
		if (max < y)
			max = y;
		if (max - y > noise)
			if (left_found)
				right_found = true;
		if (right_found) {
			if (right_min < y)
				right_min = y;
			if (y - right_min > noise) {
				msgs += tr("valley detected");
				return;
			}
		}
	}
	if (!right_found) {
		msgs += "no peak";
		return false;
	}
	return true;
}

